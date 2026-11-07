import pathlib, sys, subprocess, hashlib, json, datetime, shutil, zipfile
E=pathlib.Path(__file__).parent; ROOT=E.parents[2]; ORIGINAL=ROOT/'project'; S=pathlib.Path(r'<USER_HOME>\.agents\skills\vibecoding')
def inventory(p): return {str(x.relative_to(p)).replace('\\','/'):hashlib.sha256(x.read_bytes()).hexdigest() for x in p.rglob('*') if x.is_file()}
before=inventory(S); origbefore=inventory(ORIGINAL); (E/'skill-before-54.json').write_text(json.dumps(before,indent=2),encoding='utf-8')
commands=[]; checks=[]
def ck(name,ok,detail=None): checks.append({'name':name,'pass':bool(ok),'detail':detail})
def run(name,args,cwd=None):
    r=subprocess.run(args,cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120)
    row={'name':name,'command':args,'cwd':str(cwd or E),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}; commands.append(row)
    (E/(name+'.log')).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8'); return r
impl='''def normalize_percent(value):
    if type(value) is not int:
        raise TypeError("integer required")
    if value < 0 or value > 100:
        raise ValueError("outside 0..100")
    return value
'''
tests='''import unittest
from percent import normalize_percent
class PercentTests(unittest.TestCase):
    def test_zero(self): self.assertEqual(normalize_percent(0),0)
    def test_hundred(self): self.assertEqual(normalize_percent(100),100)
    def test_middle(self): self.assertEqual(normalize_percent(42),42)
    def test_negative(self): self.assertRaises(ValueError,normalize_percent,-1)
    def test_above(self): self.assertRaises(ValueError,normalize_percent,101)
    def test_float(self): self.assertRaises(TypeError,normalize_percent,1.0)
    def test_bool(self): self.assertRaises(TypeError,normalize_percent,True)
    def test_string(self): self.assertRaises(TypeError,normalize_percent,"42")
'''
runner='''import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
suite=unittest.defaultTestLoader.discover(str(pathlib.Path(__file__).parent),pattern="test_*.py")
result=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
'''
G=E/'fixture-good'; B=E/'fixture-mutant'; G.mkdir(); B.mkdir()
for p,code in [(G,impl),(B,impl.replace('return value\n','return value + 1\n'))]:
    (p/'percent.py').write_text(code,encoding='utf-8'); (p/'test_percent.py').write_text(tests,encoding='utf-8'); (p/'run_tests.py').write_text(runner,encoding='utf-8')
    (p/'README.md').write_text('Isolated local installed-Skill integration fixture; not a business repository. normalize_percent accepts strict integers in 0..100. Eight unittest cases; no bare assert. Mutant intentionally adds one. No Git baseline.\n',encoding='utf-8')
for label,p in [('good',G),('mutant',B)]:
    dry=run(label+'-init-dry',[sys.executable,'-I','-B',str(S/'scripts/vb_init.py'),'--project',str(p),'--json'])
    ck(label+'-dry-run-no-generated-files',dry.returncode==0 and not (p/'AGENTS.md').exists() and not (p/'.vibecoding').exists())
    apply=run(label+'-init-apply',[sys.executable,'-I','-B',str(S/'scripts/vb_init.py'),'--project',str(p),'--apply','--json'])
    ck(label+'-apply-rc0',apply.returncode==0)
    first=inventory(p)
    again=run(label+'-init-idempotent',[sys.executable,'-I','-B',str(S/'scripts/vb_init.py'),'--project',str(p),'--apply','--json'])
    ck(label+'-idempotent-byte-identical',again.returncode==0 and first==inventory(p))
    direct=run(label+'-unittest',[sys.executable,'-I','-B','run_tests.py'],p)
    expected=0 if label=='good' else 1
    ck(label+'-eight-real-tests',direct.returncode==expected and 'Ran 8 tests' in direct.stderr,{'exit_code':direct.returncode})
    verify='"'+sys.executable+'" -I -B run_tests.py'
    gate=run(label+'-gate',[sys.executable,'-I','-B',str(S/'scripts/vb_gate.py'),'--project',str(p),'--task','T-INTEGRATION-'+label.upper(),'--verify',verify,'--task-status','DONE','--check-standard'],p)
    ck(label+'-gate-expected-result',gate.returncode==expected,{'expected':expected,'actual':gate.returncode})
    evidence=p/'.vibecoding/evidence'/('T-INTEGRATION-'+label.upper()+'.md'); content=evidence.read_text(encoding='utf-8-sig')
    ck(label+'-evidence-records-real-result',('PASS' if expected==0 else 'FAIL') in content and 'run_tests.py' in content)
    hand=run(label+'-handoff',[sys.executable,'-I','-B',str(S/'scripts/vb_handoff.py'),'--project',str(p),'--task','T-INTEGRATION-'+label.upper(),'--done','Installed CLI workflow exercised on isolated fixture','--verify',f'8 unittest cases; expected exit {expected}; gate exit {gate.returncode}','--blocked','none' if expected==0 else 'Deliberate +1 mutant; tests and gate must fail','--effects','Only this new fixture written','--hygiene','No Git baseline; Python -I -B used','--next','No business or release readiness claim'])
    show=run(label+'-handoff-show',[sys.executable,'-I','-B',str(S/'scripts/vb_handoff.py'),'--project',str(p),'--show'])
    ck(label+'-handoff-write-and-show',hand.returncode==0 and show.returncode==0)
    ck(label+'-no-python-cache',not list(p.rglob('*.pyc')) and not list(p.rglob('__pycache__')))
    # -O does not remove unittest self.assert* checks; demonstrate this rather than relying on bare assert.
    opt=run(label+'-unittest-optimized',[sys.executable,'-I','-B','-O','run_tests.py'],p)
    ck(label+'-optimized-assertions-retained',opt.returncode==expected and 'Ran 8 tests' in opt.stderr)
after=inventory(S); (E/'skill-after-54.json').write_text(json.dumps(after,indent=2),encoding='utf-8')
ck('installation-tree-54-unchanged',before==after and len(before)==54,{'before_count':len(before),'after_count':len(after),'changed':[k for k in set(before)|set(after) if before.get(k)!=after.get(k)]})
cache='scripts/__pycache__/vb_trust.cpython-314.pyc'; ck('existing-cache-preserved',cache in before and before.get(cache)==after.get(cache))
ck('original-project-entirely-unchanged',origbefore==inventory(ORIGINAL))
review=(ORIGINAL/'.vibecoding/evidence/T-INIT.md').read_text(encoding='utf-8-sig')
ck('original-review-placeholders-retained','反向遗漏审查：待人工填写' in review and '审查：待人工填写' in review)
result={'time_asia_shanghai':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'scope':'Local deterministic installed CLI/Skill integration; NOT a new model-driven E2E','status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','check_count':len(checks),'passed':sum(x['pass'] for x in checks),'checks':checks,'commands':commands,'test_coverage':{'unittest_cases_per_run':8,'direct_normal_runs':2,'gate_runs':2,'optimized_runs':2,'expected_mutant_failures_per_run':3},'review_scope':{'performed':'Automated external artifact/config/block/path/manifest review, plus actual positive/negative unittest gate checks on NEW fixtures.','not_performed':'No human reviewer signoff or business acceptance; original review and reverse-omission placeholders remain.','omissions':'Original compileall covered zero .py files; new fixtures supply executable correctness/boundary/negative checks but do not retroactively replace original T-INIT acceptance command.'},'risks':['Previous whole-tree zero-write FAIL remains: historical pyc addition is not erased. Current 54-file tree unchanged is a separate interval.','First PowerShell quoting failure, interrupted model session, help mojibake remain observations.','Existing always-prefix approvals broader than one-time approval; no approval configuration read or changed.','No new model call, no repository clone/modification, no business functionality tested, no formal release signoff.','Formal release PENDING; public publication PENDING/BLOCKED.']}
(E/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 本机安装集成验证收尾','',f"时间：{result['time_asia_shanghai']}（Asia/Shanghai）",f"结果：{result['status']}；独立检查 {result['passed']}/{len(checks)}",'','本次是确定性CLI/Skill集成验证，不是新的模型驱动E2E。','正例/故障负例各含8个真实unittest用例；直接运行、门禁调用、-O运行各一轮，共6轮48个用例执行。','正例三个测试运行退出码均0；故障负例三个测试运行均预期退出1（3个断言失败）；正例gate退出0，负例gate退出1。以RESULT.json真实日志为准。','两个fixture均验证dry-run不落盘、apply成功、再次apply字节幂等、handoff写入和show。','',f'安装目录前后 {len(before)}/{len(after)} 文件；既有缓存保留且哈希不变，当前区间无新增缓存；原项目全文件哈希不变。','历史53→54缓存新增的零写入FAIL不改写。','','## 人工审查边界','已做：外部产物/配置/受管块/路径/可信清单检查及新fixture正负例集成测试。','未做：人工独立签收、业务验收；原T-INIT人工review和反向遗漏占位原样保留。','原compileall空跑缺口由新fixture补充覆盖，不倒填原证据，不伪造原会话退出码。','','## 限制']+['- '+x for x in result['risks']]
lines+=['','## 检查明细']+['- '+('PASS ' if x['pass'] else 'FAIL ')+x['name'] for x in checks]
(E/'收尾报告.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
zip_path=E.parent/(E.name+'-share.zip')
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in E.rglob('*'):
        if p.is_file(): z.write(p,str(p.relative_to(E)))
print(json.dumps({'status':result['status'],'checks':len(checks),'passed':result['passed'],'failed':[x for x in checks if not x['pass']],'evidence':str(E),'zip':str(zip_path),'command_exit_codes':{x['name']:x['exit_code'] for x in commands}},ensure_ascii=False,indent=2))
sys.exit(0 if result['status']=='PASS' else 1)
