from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from .test_artifact_contract import _candidate, contract
from .test_review_entry import entry

pytestmark = pytest.mark.deterministic
V6 = contract.CONTRACT_PATH


def candidate_v6(**kwargs):
    return _candidate(**kwargs)


@pytest.mark.parametrize('skill_class', ['primary_agent_development', 'product_agentic', 'product_hybrid', 'projection_only'])
def test_default_accepts_current_structure_and_rejects_old_layout(skill_class):
    new = candidate_v6(skill_class=skill_class)
    assert contract.validate_artifact(new).contract_version == 'skill_artifact_contract_v6'
    text = new.decode()
    first, rest = text.split('## 2. Intended Outcomes', 1)
    outcomes, rest = rest.split('## 3. Boundaries', 1)
    boundaries, rest = rest.split('## 4. Inputs and Completion', 1)
    old = (first.replace('## 1. Task Summary', '## 1. Task')
           + '## 2. Boundaries' + boundaries + '## 3. Intended Outcomes' + outcomes
           + '## 4. Inputs and Completion' + rest)
    old = old.replace('### 4.1 Inputs', '### 4.1 Inputs and Authority')
    old = old.replace('### 4.2 Output', '### 4.2 Output and Completion')
    old = old.replace('### 4.3 Completion Contract\n\nThe result meets the agreed criteria.\n\n', '')
    with pytest.raises(ValueError, match='required sections'):
        contract.validate_artifact(old.encode())


@pytest.mark.parametrize('replacement', ['', 'TODO', '<!-- no body -->', '### 4.3.1 Empty child'])
def test_completion_requires_content(replacement):
    payload = candidate_v6().replace(b'The result meets the agreed criteria.', replacement.encode())
    with pytest.raises(ValueError, match='subsection'):
        contract.validate_artifact(payload, contract_path=V6)


@pytest.mark.parametrize('replacement', ['', 'TBD', '<!-- no body -->'])
def test_main_section_requires_content(replacement):
    payload = candidate_v6().replace(b'Deliver one complete candidate for the recipient to review against its owning Design.', replacement.encode())
    with pytest.raises(ValueError, match='section is empty'):
        contract.validate_artifact(payload, contract_path=V6)


@pytest.mark.parametrize('old,new', [
    (b'### 4.1 Inputs', b'### 4.1 Inputs and Authority'),
    (b'### 4.2 Output', b'### 4.2 Output and Completion'),
    (b'### 4.3 Completion Contract', b'### 4.4 Completion Contract'),
    (b'### 4.2 Output', b'### 5.1 Output'),
])
def test_required_subsections_cannot_be_renamed_or_misnumbered(old,new):
    with pytest.raises(ValueError, match='subsection'):
        contract.validate_artifact(candidate_v6().replace(old,new), contract_path=V6)


def test_duplicate_and_moved_subsections_are_rejected():
    payload = candidate_v6()
    for suffix in (b'\n### 4.3 Completion Contract\n\nRepeated.\n',):
        with pytest.raises(ValueError, match='exactly once'):
            contract.validate_artifact(payload+suffix, contract_path=V6)
    moved = payload.replace(b'### 4.3 Completion Contract\n\nThe result meets the agreed criteria.\n\n', b'')
    moved += b'\n### 4.3 Completion Contract\n\nMoved into Method.\n'
    with pytest.raises(ValueError, match='parent'):
        contract.validate_artifact(moved, contract_path=V6)


def test_out_of_order_subsections_are_rejected():
    text = candidate_v6().decode()
    a, b = text.split('### 4.2 Output')
    output, b = b.split('### 4.3 Completion Contract')
    completion, method = b.split('## 5. Method')
    with pytest.raises(ValueError, match='out of order'):
        contract.validate_artifact((a+'### 4.3 Completion Contract'+completion+'### 4.2 Output'+output+'## 5. Method'+method).encode(),contract_path=V6)


def test_optional_author_rules_supplements_and_fenced_examples():
    payload = candidate_v6(authoring_section=True)
    payload = payload.replace(b'## 5. Method', b'### 4.4 Additional task material\n\nUseful extra material.\n\n## 5. Method')
    payload += b'\n```md\n## 1. Task\n### 4.1 Inputs and Authority\n```\n\n## 6. Appendix\n\nUseful reference.\n\n### 6.1 Example\n\nContent.\n'
    result = contract.validate_artifact(payload,contract_path=V6,embedded_resource_ids=('soul:bestpractice_ai_facing_writing',))
    assert result.headings[-1]=='Appendix'


def test_unknown_contract_version_and_invalid_subsection_definition(tmp_path):
    definition=json.loads(V6.read_text())
    for key,value in [('contract_version','skill_artifact_contract_v5'),('contract_version','skill_artifact_contract_v999'),('required_sections',definition['required_sections'][:3])]:
        invalid={**definition,key:value};p=tmp_path/'contract.json';p.write_text(json.dumps(invalid))
        with pytest.raises(ValueError):contract.validate_artifact(candidate_v6(),contract_path=p)
    definition['required_sections'][3]['required_subsections'][2]['index']='9.1'
    p.write_text(json.dumps(definition))
    with pytest.raises(ValueError,match='subsection'):contract.load_contract(p)


def test_cli_reports_selected_contract_and_default_published_version(tmp_path):
    for payload,selected,version in [(candidate_v6(),None,'v6'),(candidate_v6(),V6,'v6')]:
        candidate=tmp_path/'SKILL.md';candidate.write_bytes(payload)
        args=[sys.executable,'-B',str(entry.HERE/'skill_review.py'),'--candidate',str(candidate),'--check-only','--project-root',str(tmp_path)]
        if selected:args+=['--contract',str(selected)]
        result=subprocess.run(args,capture_output=True,text=True,check=True)
        report=json.loads(result.stdout)
        assert report['contract_version']=='skill_artifact_contract_'+version
        expected=hashlib.sha256((selected or contract.CONTRACT_PATH).read_bytes()).hexdigest()
        assert report['artifact_contract_sha256']==expected


def test_selected_rule_is_frozen_in_review_input(tmp_path):
    candidate=tmp_path/'SKILL.md';candidate.write_bytes(candidate_v6())
    selected=tmp_path/'v6.json';selected.write_bytes(V6.read_bytes())
    authority=tmp_path/'09_soul/governance/t0/the_skill_management.md';authority.parent.mkdir(parents=True);authority.write_text('Fixture authority.')
    ids=[x['check_id'] for x in contract.load_contract(V6)['reviewer_checklist']['checks']]
    sc=tmp_path/'self_check.json';sc.write_text(json.dumps({'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'rows':[{'check_id':i,'exact_evidence':'Fixture section.','local_result':'Checked.','unresolved_finding':None} for i in ids]}))
    payload,frozen=entry._prepare(candidate_path=candidate,goal='Fixture task',change='Fixture structure',self_check_path=sc,project_root=tmp_path,contract_path=selected)
    inspection=json.loads(next(x['body'] for x in payload['source_and_projection_closure'] if x['document_id']=='candidate_checks'))
    assert inspection['contract_version']=='skill_artifact_contract_v6'
    assert selected in frozen
    selected.write_bytes(selected.read_bytes()+b'\n')
    with pytest.raises(ValueError,match='input or path binding changed'):entry._assert_frozen(frozen)


@pytest.mark.parametrize('example', ['```md\n## Literal heading\n```', '~~~html\n<!-- Literal example -->\n~~~'])
def test_fenced_example_content_is_not_prose_scaffolding(example):
    payload=candidate_v6().replace(b'The result meets the agreed criteria.',example.encode())
    assert contract.validate_artifact(payload,contract_path=V6).contract_version=='skill_artifact_contract_v6'


@pytest.mark.parametrize('heading', ['## Unnumbered section', '### Unnumbered subsection'])
def test_skill_owned_headings_require_numbers(heading):
    with pytest.raises(ValueError, match='heading must use'):
        contract.validate_artifact(candidate_v6()+('\n'+heading+'\n\nContent.\n').encode(),contract_path=V6)


def test_declared_resource_headings_are_not_skill_owned():
    resource='soul:bestpractice_ai_facing_writing'
    block=f'<!-- embedded-resource:{resource}:start -->\n## Resource heading\n\nContent.\n\n### Resource child\n\nContent.\n<!-- embedded-resource:{resource}:end -->'
    payload=candidate_v6(authoring_section=True).replace(b'Use the registered common authoring instruction.',block.encode())
    assert contract.validate_artifact(payload,contract_path=V6,embedded_resource_ids=(resource,)).headings[0]=='AI-facing Authoring Rules'


@pytest.mark.parametrize('expected,old,new', [
    ('Task Summary', b'## 1. Task Summary', b'## 1. Task'),
    ('Intended Outcomes', b'## 2. Intended Outcomes', b'## 2. Boundaries'),
])
def test_v6_error_identifies_expected_and_observed_main_heading(expected,old,new):
    with pytest.raises(ValueError) as error:
        contract.validate_artifact(candidate_v6().replace(old,new),contract_path=V6)
    message=str(error.value)
    assert expected in message and 'expected' in message and 'observed' in message
    assert new.decode().split('. ',1)[1] in message


def test_v6_error_identifies_duplicate_heading():
    with pytest.raises(ValueError,match="duplicated:.*Method"):
        contract.validate_artifact(candidate_v6()+b'\n## 6. Method\n\nDuplicate.\n',contract_path=V6)


def test_v6_error_identifies_subsection_order():
    text=candidate_v6().decode()
    a,b=text.split('### 4.2 Output');output,b=b.split('### 4.3 Completion Contract');completion,method=b.split('## 5. Method')
    with pytest.raises(ValueError) as error:
        contract.validate_artifact((a+'### 4.3 Completion Contract'+completion+'### 4.2 Output'+output+'## 5. Method'+method).encode(),contract_path=V6)
    message=str(error.value)
    assert 'out of order' in message and 'expected' in message and 'observed' in message
    assert '4.2' in message and 'Output' in message and '4.3' in message and 'Completion Contract' in message
