#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
from ScenarioGenerator.ScenarioGen import ScenarioGen,NumTable,log
import copy,itertools,random

class ImpNumTable(NumTable):
    def __init__(self,vals,suit_ct,cnum_ct,depth=0):
        self.vals=vals
        self.suit_ct=suit_ct
        self.cnum_ct=cnum_ct
        self.depth=depth

    def breed(self):
        col_num=self.depth%3 #column number
        row_num=self.depth//3
        if self.vals[self.depth]>=0:
            if not self.check(col_num,row_num,self.vals):
                return False
            if self.depth==11:
                #self.re_list.append(self.vals)
                return True
            else:
                self.depth+=1
                return self.breed()
        else:
            for i in range(0,min(self.cnum_ct[col_num],self.suit_ct[row_num])+1):
                neo_vals=copy.copy(self.vals)
                neo_vals[self.depth]=i
                if not self.check(col_num,row_num,neo_vals):
                    continue
                #depth first
                if self.depth==11:
                    #self.re_list.append(neo_vals)
                    return True
                else:
                    child=ImpNumTable(neo_vals,self.suit_ct,self.cnum_ct,depth=self.depth+1)
                    if child.breed():
                        return True
        return False

class ImpScenarioGen(ScenarioGen):
    def __init__(self,myseat,history,cards_on_table,cards_list,thisuit,level=2,num_per_imp=2,imp_cards=None,METHOD1_PREFERENCE=0):
        """
            myseat, history and cards_on_table will be fed to gen_void_info to get void_info
            history, cards_on_table and cards_list will be fed to gen_cards_remain to get cards_remain
            cards_list: cards in my hand
            level: the number of important cards to be considered
        """

        #void_info and cards_remain are all in relative order!
        self.void_info=ScenarioGen.gen_void_info(myseat,history,cards_on_table)
        self.cards_remain=ScenarioGen.gen_cards_remain(history,cards_on_table,cards_list)
        #确认别人手里牌的数量和我手里的还有桌上牌的数量相符
        assert len(self.cards_remain)==3*len(cards_list)-(len(cards_on_table)-1)

        #lens is like [[13],[12],[12]], also in relative order like void_info and cards_remain
        if len(cards_on_table)==1: #If I am the first
            self.lens=[len(cards_list),2*len(cards_list),3*len(cards_list)]
        elif len(cards_on_table)==2: #I am the second one
            self.lens=[len(cards_list),2*len(cards_list),3*len(cards_list)-1]
        elif len(cards_on_table)==3: #I am the third one
            self.lens=[len(cards_list),2*len(cards_list)-1,3*len(cards_list)-2]
        elif len(cards_on_table)==4: #I am the last one
            self.lens=[len(cards_list)-1,2*len(cards_list)-2,3*len(cards_list)-3]

        self.thisuit=thisuit
        self.level=level
        self.num_per_imp=num_per_imp
        self.imp_cards=imp_cards
        self.METHOD1_PREFERENCE=METHOD1_PREFERENCE
        self.init_continue()

    def init_continue(self):
        if self.imp_cards==None:
            self.imp_cards=self.decide_imp_cards()
        else:
            self.level=len(self.imp_cards)

        if len(self.imp_cards)==0:
            self.number=(3**self.level)*self.num_per_imp
            self.exhaust_threshold=self.number*2
            s_temp=''.join((i[0] for i in self.cards_remain))
            self.suit_ct=[s_temp.count(s) for s in "SHDC"] #suit remain number count
            self.reinforce_void_info()
            self.decide_method()
            if self.method==0:
                self.scenarios=[self.shot_and_test() for i in range(self.number)]
            elif self.method==1:
                self.scenarios=[self.construct_by_table() for i in range(self.number)]
            elif self.method==2:
                self.scenarios=self.exhaustive
            else:
                raise Exception("method error")
        else:
            for c in self.imp_cards:
                self.cards_remain.remove(c)
            self.number=self.num_per_imp #for decide_method
            self.exhaust_threshold=self.number*2
            self.construct_wrt_imp()

    def __iter__(self):
        return self.scenarios.__iter__()

    def get_scenarios(self):
        return self.scenarios

    def decide_imp_cards(self):
        """
            decide at most self.level number of most important cards
            TODO: make this decision adaptive
        """
        if self.thisuit=="A":
            potential_imp_cards=[]
            if "SQ" in self.cards_remain:
                potential_imp_cards+=["SQ","SA","SK"]
            if "DJ" in self.cards_remain:
                potential_imp_cards+=["DJ","DA","DK","DQ"]
            if True:
                potential_imp_cards+=["HA","HK","HQ"]
            if "C10" in self.cards_remain:
                potential_imp_cards+=["C10","CA","CK","CQ","CJ"]
        elif self.thisuit=="S":
            potential_imp_cards=["SQ","SA","SK","SJ","S10"]
        elif self.thisuit=="H":
            potential_imp_cards=["HA","HK","HQ","HJ","H10"]
        elif self.thisuit=="D":
            potential_imp_cards=["DJ","DA","DK","DQ","D10"]
        elif self.thisuit=="C":
            potential_imp_cards=["C10","CA","CK","CQ","CJ"]

        imp_cards=[c for c in potential_imp_cards if c in self.cards_remain]
        imp_cards=imp_cards[0:min(self.level,len(imp_cards))]
        #log("imp cards: %s %s"%(imp_cards,potential_imp_cards))
        return imp_cards

    def add_imp_cards(self,cards_list_list,distribution):
        for i in range(len(distribution)):
            cards_list_list[distribution[i]].append(self.imp_cards[i])
        return cards_list_list

    def check_distribution(self,distribution):
        cards_list_list=self.add_imp_cards([[],[],[]],distribution)
        if not ScenarioGen.check_void_legal(cards_list_list[0],cards_list_list[1],cards_list_list[2],self.void_info):
            return False
        cnum_ct=[0,0,0]
        for i in distribution:
            cnum_ct[i]+=1
        if cnum_ct[0]>self.lens[0]:
            return False
        elif cnum_ct[1]>self.lens[1]-self.lens[0]:
            return False
        elif cnum_ct[2]>self.lens[2]-self.lens[1]:
            return False
        return True

    def construct_wrt_imp(self):
        distributions=[d for d in itertools.product([0,1,2],repeat=len(self.imp_cards))\
                         if self.check_distribution(d)]
        compensate=(3**self.level)//len(distributions)
        self.num_per_imp*=compensate
        self.number*=compensate
        s_temp=''.join((i[0] for i in self.cards_remain))
        self.suit_ct=[s_temp.count(s) for s in "SHDC"]

        self_bk=copy.deepcopy(self)
        scenarios=[]
        for distribution in distributions:
            #log("considering: %s"%(distribution,))
            scegen=copy.deepcopy(self_bk)
            for i in distribution:
                for j in range(i,3):
                    scegen.lens[j]-=1
            #higher order interaction
            cnum_ct=[scegen.lens[0],scegen.lens[1]-scegen.lens[0],scegen.lens[2]-scegen.lens[1]]
            scegen.reinforce_void_info()
            val_dict={True:0,False:-1}
            vals=[val_dict[scegen.void_info[0]['S']],val_dict[scegen.void_info[1]['S']],val_dict[scegen.void_info[2]['S']],
                  val_dict[scegen.void_info[0]['H']],val_dict[scegen.void_info[1]['H']],val_dict[scegen.void_info[2]['H']],
                  val_dict[scegen.void_info[0]['D']],val_dict[scegen.void_info[1]['D']],val_dict[scegen.void_info[2]['D']],
                  val_dict[scegen.void_info[0]['C']],val_dict[scegen.void_info[1]['C']],val_dict[scegen.void_info[2]['C']],]
            nt_root=ImpNumTable(vals,self.suit_ct,cnum_ct)
            if not nt_root.breed():
                #log("eliminate %s because of 2nd order int:\n%s\n%s\n%s\n%s"%(distribution,self.cards_remain,self.void_info,self.lens,scegen.lens),end="");input()
                continue
            scegen.decide_method()
            #log("decided method to be: %d"%(scegen.method))

            if scegen.method==0:
                for i in range(self.num_per_imp):
                    scenarios.append(self.add_imp_cards(scegen.shot_and_test(),distribution))
            elif scegen.method==1:
                for i in range(self.num_per_imp):
                    scenarios.append(self.add_imp_cards(scegen.construct_by_table(),distribution))
            elif scegen.method==2:
                for cll in random.sample(scegen.exhaustive,min(self.num_per_imp,len(scegen.exhaustive))):
                    scenarios.append(self.add_imp_cards(cll,distribution))
            else:
                raise Exception("method error")

            #log("got new scenarios: %s"%(scenarios[-1*self.num_per_imp:]),end="");input()

        for cards_list_list in scenarios:
            assert ScenarioGen.check_void_legal(cards_list_list[0],cards_list_list[1],cards_list_list[2],self.void_info)
            assert len(cards_list_list[0])==self.lens[0]
            assert len(cards_list_list[1])==self.lens[1]-self.lens[0]
            assert len(cards_list_list[2])==self.lens[2]-self.lens[1]

        #log("get %d scenarios"%(len(scenarios)))
        self.scenarios=scenarios

    def decide_method(self):
        #s_temp=''.join((i[0] for i in self.cards_remain))
        #self.suit_ct=[s_temp.count(s) for s in "SHDC"] #suit remain number count
        #self.reinforce_void_info()
        #predict success rate
        cell_num=[sum((1 for j in range(3) if not self.void_info[j]['S'])),sum((1 for j in range(3) if not self.void_info[j]['H'])),
                  sum((1 for j in range(3) if not self.void_info[j]['D'])),sum((1 for j in range(3) if not self.void_info[j]['C']))]
        self.suc_rate_predict=1
        self.tables_num_predict=1
        for i in range(4):
            self.suc_rate_predict*=(cell_num[i]/3)**(self.suit_ct[i])
            self.tables_num_predict*=ScenarioGen.C(self.suit_ct[i]+cell_num[i]-1,cell_num[i]-1)
        col_res=1
        for j in range(3):
            p_suit=[self.suit_ct[i] for i in range(4) if not self.void_info[j]['SHDC'[i]]]
            if len(p_suit)>0:
                col_res*=(max(p_suit)+1)
        self.tables_num_predict/=col_res**(2/3)

        method0_time=(0.63*len(self.cards_remain)+1.01)/self.suc_rate_predict
        method1_time=self.tables_num_predict*80/self.number+25
        if method1_time-self.METHOD1_PREFERENCE<method0_time:
            self.method=1
            self.gen_num_tables()
        else:
            self.method=0
            self.tot_ct=0 #total try counter

def test():
    s=ImpScenarioGen(0,[[0,'S2','S3','S4','S5'],[0,'S6','S7','S8','S9'],[0,'S10','SJ','SQ','SK'],
                     [0,'H2','H3','H4','H5'],[0,'H6','H7','H8','H9'],[0,'H10','CJ','HQ','HK'],
                     [0,'C2','C3','C4','C5'],[0,'C6','C7','C8','C9'],[0,'C10','HJ','CQ','D6'],]
                    ,[2,'SA','HA'],['D2','D3','D4','D5'],imp_cards=["CA","DJ"],METHOD1_PREFERENCE=10000)
    log(s.void_info)
    log(s.scenarios)

if __name__=="__main__":
    test()