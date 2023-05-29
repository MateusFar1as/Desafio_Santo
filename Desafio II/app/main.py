from fastapi import FastAPI, HTTPException, status
import sqlalchemy as db
from pydantic import BaseModel
from decimal import Decimal

engine = db.create_engine("mysql+mysqldb://root:123456@mysql:3306/adventure")
metadata = db.MetaData()
connection = engine.connect()

app = FastAPI()

# ---------------------------- Tarefa 01 ----------------------------

table_prod = db.Table( "products", metadata, autoload_with=engine)
chaves = table_prod.columns.keys()

class Produto(BaseModel):
    sku: str
    nome: str
    nomeModelo: str
    descricao: str
    cor: str
    tamanho: str
    estilo: str
    custo: float
    preco: float
    subCategoria: int


@app.post("/products/", status_code=status.HTTP_201_CREATED)
async def criar_produto(p: Produto):

    query = table_prod.insert().values(
        ProductSKU = p.sku,
        ProductName = p.nome,
        ModelName = p.nomeModelo,
        ProductDescription = p.descricao,
        ProductColor = p.cor,
        ProductSize = p.tamanho,
        ProductStyle = p.estilo,
        ProductCost = p.custo,
        ProductPrice = p.preco,
        ProductSubcategoryKey = p.subCategoria
    )

    result = connection.execute(query)
    connection.commit()

    return {"mensagem" : "Produto criado com sucesso"}


@app.get("/products/{ProductKey}", status_code=status.HTTP_200_OK)
async def visualizar_produto_pela_id(ProductKey):
    query = db.select(table_prod).where(table_prod.c.ProductKey == ProductKey)   
    
    result = connection.execute(query).fetchall()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Produto com id {ProductKey} nao existe!!")
    
    chaves = table_prod.columns.keys()
    dados = [{
        chaves[i]: float(row[i]) if isinstance(row[i], Decimal) else row[i]
        for i in range(len(chaves))
    }
    for row in result
    ]

    return {"Produto" : dados}

@app.get("/products/", status_code=status.HTTP_200_OK)
async def visualizar_produtos():
    query = db.select(table_prod)  
    
    result = connection.execute(query).fetchall()

    chaves = table_prod.columns.keys()
    dados = [{
        chaves[i]: float(row[i]) if isinstance(row[i], Decimal) else row[i]
        for i in range(len(chaves))
    }
    for row in result
    ]

    return {"Produtos" : dados}


@app.put("/products/{ProductKey}", status_code=status.HTTP_202_ACCEPTED)
async def editar_produto_pela_id(ProductKey, p: Produto):
    query = db.update(table_prod).where(table_prod.c.ProductKey == ProductKey).values(
        ProductSKU = p.sku,
        ProductName = p.nome,
        ModelName = p.nomeModelo,
        ProductDescription = p.descricao,
        ProductColor = p.cor,
        ProductSize = p.tamanho,
        ProductStyle = p.estilo,
        ProductCost = p.custo,
        ProductPrice = p.preco,
        ProductSubcategoryKey = p.subCategoria
    )

    result = connection.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Produto com id {ProductKey} nao existe!!")
    connection.commit()

    return {"mensagem" : "Produto editado com sucesso"}


@app.delete("/products/{ProductKey}", status_code=status.HTTP_202_ACCEPTED)
async def deletar_produto_pela_id(ProductKey):
    query = db.delete(table_prod).where(table_prod.c.ProductKey == ProductKey)   

    result = connection.execute(query)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Produto com id {ProductKey} nao existe!!")

    connection.commit()

    return {"mensagem" : "Produto deletado com sucesso"}

# --------------------------------------------------------------------


# ---------------------------- Tarefa 02 ----------------------------

# Rota que retorna os 10 produtos mais vendidos na categoria fornecida.
@app.get("/sales/top-products/category/{category}", status_code=status.HTTP_200_OK)
async def top10_produtos_mais_vendidos(category):
    query = db.text(f"""
    select comb.ProductKey, comb.ProductName, sum(vendas) as total_vendas from(
    select prod.ProductKey, prod.ProductName, count(prod.ProductKey) as vendas from products as prod 
    inner join product_subcategories as ps on ps.ProductSubcategoryKey = prod.ProductSubcategoryKey
    inner join sales_2016 as s16 on s16.ProductKey = prod.ProductKey where ps.ProductCategoryKey = {category}
    group by prod.Productkey
    union all
    select prod.ProductKey, prod.ProductName, count(prod.ProductKey) as vendas from products as prod 
    inner join product_subcategories as ps on ps.ProductSubcategoryKey = prod.ProductSubcategoryKey
    inner join sales_2017 as s17 on s17.ProductKey = prod.ProductKey where ps.ProductCategoryKey = {category}
    group by prod.Productkey
    union all
    select prod.ProductKey, prod.ProductName, count(prod.ProductKey) as vendas from products as prod 
    inner join product_subcategories as ps on ps.ProductSubcategoryKey = prod.ProductSubcategoryKey
    inner join sales_2015 as s15 on s15.ProductKey = prod.ProductKey where ps.ProductCategoryKey = {category}
    group by prod.Productkey
    ) as comb group by comb.ProductKey, comb.ProductName order by total_vendas desc limit 10;
    """)

    result = connection.execute(query)
    
    dados = [{"Id_Produto" : row[0], "Produto" : row[1], "Vendas_totais" : row[2]} for row in result]

    return dados


# Rota que retorna o cliente com o maior número de pedidos realizados.
@app.get("/sales/best-customer/", status_code=status.HTTP_200_OK)
async def cliente_com_mais_pedidos():
    query = db.text("""
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
    """)

    result = connection.execute(query)
    
    dados = [{"Id_Cliente" : row[0], "Primeiro_Nome" : row[1], "Ultimo_Nome" : row[2], "Compras_Totais" : row[3]} for row in result]

    return dados


# Rota que retorna o mês com mais vendas (em valor total).
@app.get("/sales/busiest-month/", status_code=status.HTTP_200_OK)
async def mes_com_mais_venda():
    query = db.text("""
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
    """)

    result = connection.execute(query)
    
    dados = [{"Mes" : row[0], "Valor_Total" : row[1]} for row in result]

    return dados


# Rota que retorna os vendedores que tiveram vendas com valor acima da média no último ano fiscal.
@app.get("/sales/top-territories/", status_code=status.HTTP_200_OK)
async def territorios_com_vendas_acima_da_media():
    query = db.text("""
    select s16.TerritoryKey, round(sum(prod.ProductPrice),2) as valor_acima_media from sales_2016 as s16
    inner join products as prod on prod.ProductKey = s16.Productkey group by s16.TerritoryKey
    having round(sum(prod.ProductPrice),2) >= (
    select round(sum(prod.ProductPrice),2) / count(distinct TerritoryKey) as valor from sales_2016 as s16
    inner join products as prod on prod.ProductKey = s16.Productkey
    ) order by valor_acima_media desc;
    """)

    result = connection.execute(query)
    
    dados = [{"Id_Territorio" : row[0], "Valor_Total" : row[1]} for row in result]

    return dados