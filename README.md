# Scenario Generator

### 使用方法
Currently contains two class, `ScenarioGen` and `ImpScenarioGen`
```
sce_gen = ScenarioGen(self.place,self.history,self.cards_on_table,self.cards_list,number=sce_num,method=None,METHOD1_PREFERENCE=0,exhaust_threshold=None)
for cards_list_list in sce_gen:
    print(cards_list_list) #[["H2","SA"],["H3","H4"],["H6"."H5"]] in relative order
```

```
sce_gen = ImpScenarioGen(self.place,self.history,self.cards_on_table,self.cards_list,level=2,num_per_imp=2,imp_cards=None,METHOD1_PREFERENCE=0)
scenarios = sce_gen.get_scenarios()
# Or
for cards_list_list in sce_gen:
    print(cards_list_list)
```

### ScenarioGen

默认使用*shot and test*方法生成Scenario，在程序中*shot and test*对应`method=0`。*shot and test*是指，先随机发牌（*shot*），再测试其是否满足历史的断门的约束（*test*）。但是随着游戏进行，约束慢慢变多，*shot and test*的成功率会越来越低，甚至经常低至1%以下。为弥补*shot and test*的不足，*construct by table*方法被开发，在代码中它对应`method=1`。其中的*table*是指4x3的约束表，*construct by table*会首先通过树搜索找到所有满足约束的*table*并记录下来，在需要Scenario时，再随机抽取*table*之后根据*table*构造Scenario。如果构造出所有的*table*后发现所有可能scnario数量很小，具体而言，小于`exhaust_threshold`，那么就会穷尽所有可能情况，在代码中这对应`method=2`。`exhaust_threshold`默认为`number*2`，当然也可以自己指定。无论是哪种方法，都能保证采样是绝对均匀的。

可以在构造函数中自行指定`method`，如果不做指定，程序会自动选择。它首先会估计*shot and test*方法的成功率并计算出*shot and test*方法每生成一个Scenario所需的时间，之后他会估计所有*table*的数目并计算出*construct by table*方法每生成一个Scenario的时间，挑选二者中更好的使用。`METHOD1_PREFERENCE`设置了对*construct by table*方法的倾向，单位为us，为正时倾向*construct by table*。

经过测试，ScenarioGen每生成一个scenario的时间约为0.18ms。

### ImpScenarioGen

Variety sampling version of ScenarioGen.
