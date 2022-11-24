#Массив рецептов на каждую подкатегорию ['','','','',''],
#по 15 рецептов хватит, а то их много. очень.
#префикс urlnum обзоначает массивы с url рецептов соответсвующей категории
#вообще нужно автоматизировать, чтобы названия рецептов предоставлялись
#в режиме online прямо с сайта
soup_hot_borsh = [
    ['Борщ','Самый красный борщ','Украинский борщ от тети Нюси','Борщ по-петровски','Украинский борщ с пампушками'],
    ['Борщ от Пал Саныча','Борщ "Дивской"',' Кубанский борщ с фасолью и черносливом','Борщ по рецепту «Еврейской мамы»','Украинский борщ в горшочке с пампушками'],
    ['Борщ с грибами и стручковой фасолью','Борщ по-польски','Костин борщ','"Жареный" борщ','Борщ для здорового питания']
]
urlnum_soup_hot_borsh = [
    ['25436','63955','96329','123061','12169'],
    ['79370','66321','25920','172144','153711'],
    ['42220','149871','160051','64084','75299']
]
soup_hot_shi = [
    ['Щи "Успенские" с солеными огурцами','Щи по-уральски','Щи кислые "Обыкновенные"','Просто щи','Суп "Дед"'],
    ['Щи валаамские','Щи из свежей капусты','Щи постные с фасолью','Молочные щи','Щи "Старославянские"'],
    ['Щи "Бабушкины"','Кислые щи из квашеной капусты','Толстые щи с квашеной капустой','Щи "По-монастырски"','Капустный суп с фасолью']
]
urlnum_soup_hot_shi = [
    ['103935','107129','119535','22131','148773'],
    ['154731','7536','149585','60790','137714'],
    ['177194','14581','149423','51777','144546']
]
sauce_domashniy_maionez = [
    ['Соус а-ля майонез "Юлия" на молоке','Майонез','Майонез домашний','Майонез «Домашний», который всегда получается','Постный майонез'],
    ['Вегетарианский рисовый майонез','Майонез с чесноком, огурцом и имбирём','Вегетарианский майонез из аквафабы','Постный майонез "Новогоднее настроение"','Постный веганский майонез и нутово-морковные котлеты'],
    ['Майонез домашний','Соус яблочный к салатам и закускам','Постный соус "Провансаль"','Испанский чесночный майонез "Алиоли"','Домашний майонез без яиц']
]
urlnum_sauce_domashniy_maionez = [
    ['34105','43906','24063','40524','124020'],
    ['119389','119326','142512','70169','64252'],
    ['73418','174111','58377','110998','152135']
]