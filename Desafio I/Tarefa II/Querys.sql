# 1º PERGUNTA
select comb.ProductKey, comb.ProductName, sum(vendas) as total_vendas from(
select prod.ProductKey, prod.ProductName, count(prod.ProductKey) as vendas from products as prod 
inner join product_subcategories as ps on ps.ProductSubcategoryKey = prod.ProductSubcategoryKey
inner join sales_2016 as s16 on s16.ProductKey = prod.ProductKey where ps.ProductCategoryKey = 1
group by prod.Productkey
union all
select prod.ProductKey, prod.ProductName, count(prod.ProductKey) as vendas from products as prod 
inner join product_subcategories as ps on ps.ProductSubcategoryKey = prod.ProductSubcategoryKey
inner join sales_2017 as s17 on s17.ProductKey = prod.ProductKey where ps.ProductCategoryKey = 1
group by prod.Productkey
union all
select prod.ProductKey, prod.ProductName, count(prod.ProductKey) as vendas from products as prod 
inner join product_subcategories as ps on ps.ProductSubcategoryKey = prod.ProductSubcategoryKey
inner join sales_2015 as s15 on s15.ProductKey = prod.ProductKey where ps.ProductCategoryKey = 1
group by prod.Productkey
) as comb group by comb.ProductKey, comb.ProductName order by total_vendas desc limit 10;


# 2º PERGUNTA
select comb.CustomerKey, comb.FirstName, comb.LastName, sum(compras) as total_compras from(
select cus.CustomerKey, cus.FirstName, cus.LastName, count(cus.CustomerKey) as compras from customers as cus
inner join sales_2015 as s15 on s15.CustomerKey = cus.CustomerKey
group by cus.CustomerKey
union all
select cus.CustomerKey, cus.FirstName, cus.LastName, count(cus.CustomerKey) as compras from customers as cus
inner join sales_2016 as s16 on s16.CustomerKey = cus.CustomerKey
group by cus.CustomerKey
union all
select cus.CustomerKey, cus.FirstName, cus.LastName, count(cus.CustomerKey) as compras from customers as cus
inner join sales_2017 as s17 on s17.CustomerKey = cus.CustomerKey
group by cus.CustomerKey
)as comb group by comb.CustomerKey, comb.FirstName, comb.LastName order by total_compras desc limit 1;


# 3º PERGUNTA
select comb.mes, sum(valor) as total_valor from(
select month(str_to_date(s15.OrderDate, '%m/%d/%Y')) as mes, round(sum(prod.ProductPrice),2) as valor from sales_2015 as s15
inner join products as prod on prod.ProductKey = s15.ProductKey group by mes
union all
select month(str_to_date(s16.OrderDate, '%m/%d/%Y')) as mes, round(sum(prod.ProductPrice),2) as valor from sales_2016 as s16
inner join products as prod on prod.ProductKey = s16.ProductKey group by mes
union all
select month(str_to_date(s17.OrderDate, '%m/%d/%Y')) as mes, round(sum(prod.ProductPrice),2) as valor from sales_2017 as s17
inner join products as prod on prod.ProductKey = s17.ProductKey group by mes
)as comb group by comb.mes order by total_valor desc limit 1;


# 4º PERGUNTA
select s16.TerritoryKey, round(sum(prod.ProductPrice),2) as valor_acima_media from sales_2016 as s16
inner join products as prod on prod.ProductKey = s16.Productkey group by s16.TerritoryKey
having round(sum(prod.ProductPrice),2) >= (
select round(sum(prod.ProductPrice),2) / count(distinct TerritoryKey) as valor from sales_2016 as s16
inner join products as prod on prod.ProductKey = s16.Productkey
) order by valor_acima_media desc;


# EXTRA (QUAIS OS 5 PRODUTOS QUE MAIS TIVERAM RETORNOS)
select prod.ProductKey, prod.ProductName, prod.ModelName, count(ret.ProductKey) as Total_retornos from returns as ret
inner join products as prod on prod.ProductKey = ret.ProductKey
group by prod.Productkey order by Total_retornos desc limit 5;