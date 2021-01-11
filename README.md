### Scenario Generator

Currently contains two class, `ScenarioGen` and `ImpScenarioGen`
```
sce_gen = ScenarioGen(self.place,self.history,self.cards_on_table,self.cards_list,number=sce_num,method=None,METHOD1_PREFERENCE=0,exhaust_threshold=None)
for cards_list_list in sce_gen:
    print(cards_list_list) #[["H2","SA"],["H3","H4"],["H6"."H5"],["H7","H8"]] in absolute order
```

```
sce_gen = ImpScenarioGen(self.place,self.history,self.cards_on_table,self.cards_list,level=2,num_per_imp=2,imp_cards=None,METHOD1_PREFERENCE=0)
scenarios = sce_gen.get_scenarios()
# Or
for cards_list_list in sce_gen:
    print(cards_list_list)
```