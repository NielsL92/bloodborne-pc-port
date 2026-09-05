import json
import unittest
from tools.cfg_derive_control import prove,model_nodes

class ControlProofTests(unittest.TestCase):
    def test_both_branches_need_terminal(self):
        self.assertIsNone(prove({1:[2,3],2:[],3:None},[1],{2}))
        self.assertEqual(prove({1:[2,3],2:[],3:[]},[1],{2,3}),[1,2,3])
    def test_cycles_do_not_prove_termination(self):
        self.assertIsNone(prove({1:[2],2:[1]},[1],set()))
    def test_missing_successor_rejects(self):
        self.assertIsNone(prove({1:[2,3],2:[]},[1],{2}))
    def test_landing_pad_return_rejects(self):
        self.assertIsNone(prove({1:[2],2:[],3:None},[1,3],{2}))
    def test_terminal_suppresses_only_its_fallthrough(self):
        self.assertEqual(prove({1:[2],2:[3],3:None},[1],{2}),[1,2])
    def test_conditional_external_import_is_not_dropped(self):
        symbol=json.dumps(dict(nid='nr',library='lib',module='provider'))
        rows=[(1,1,'','je'),(2,1,'','call')]
        edges={1:[('test',100,'import_contract_unvalidated',symbol),('test',2,'fallthrough','')],2:[('test',200,'annotated_control_contract_requires_runtime','base')]}
        nodes,terminals,_=model_nodes('test',rows,edges,{}, {('nr','lib','provider'):['nr']})
        self.assertIsNone(prove(nodes,[1],terminals))
    def test_indirect_call_before_terminal_is_inconclusive(self):
        rows=[(1,1,'','call'),(2,1,'','call')]
        edges={1:[('test',None,'unresolved_indirect_call','rax'),('test',2,'fallthrough','')],2:[('test',200,'annotated_control_contract_requires_runtime','base')]}
        nodes,terminals,_=model_nodes('test',rows,edges,{}, {})
        self.assertIsNone(prove(nodes,[1],terminals))
    def test_final_call_without_contract_is_inconclusive(self):
        nodes,terminals,_=model_nodes('test',[(1,1,'','call')],{1:[('test',100,'direct_call',''),('test',2,'fallthrough','')]},{},{})
        self.assertIsNone(prove(nodes,[1],terminals))
    def test_unconditional_contract_call_is_terminal(self):
        nodes,terminals,_=model_nodes('test',[(1,1,'','call')],{1:[('test',100,'direct_call',''),('test',2,'fallthrough','')]},{('test',100):['base']},{})
        self.assertEqual(prove(nodes,[1],terminals),[1])

if __name__=='__main__':unittest.main()
