from fastapi.testclient import TestClient
from main import app, table_prod, connection, db
from decimal import Decimal

client = TestClient(app)


# ---------------------------- Tarefa 01 ----------------------------

def test_criar_produto():
    p = {
        "sku": "string",
        "nome": "string",
        "nomeModelo": "string",
        "descricao": "string",
        "cor": "string",
        "tamanho": "string",
        "estilo": "string",
        "custo": 0,
        "preco": 0,
        "subCategoria": 1
    }

    response = client.post("/products/", json = p)

    assert response.status_code == 201
    assert response.json() == {"mensagem": "Produto criado com sucesso"}


def test_visualizar_produto_pela_id():
    response = client.get("/products/600")
    assert response.status_code == 200
    assert response.json() == {
        "Produto": [
            {
            "ProductKey": 600,
            "ProductSKU": "BK-M18B-52",
            "ProductName": "Mountain-500 Black, 52",
            "ModelName": "Mountain-500",
            "ProductDescription": "Suitable for any type of riding, on or off-road. Fits any budget. Smooth-shifting with a comfortable ride.",
            "ProductColor": "Black",
            "ProductSize": "52",
            "ProductStyle": "U",
            "ProductCost": 294.5797,
            "ProductPrice": 539.99,
            "ProductSubcategoryKey": 1
            }
        ]
    }


    response = client.get("/products/5000")
    assert response.status_code == 404
    assert response.json() == {"detail": "Produto com id 5000 nao existe!!"}


def test_visualizar_produtos():
    query = db.select(table_prod)  
    
    result = connection.execute(query).fetchall()

    chaves = table_prod.columns.keys()
    dados = [{
        chaves[i]: float(row[i]) if isinstance(row[i], Decimal) else row[i]
        for i in range(len(chaves))
    }
    for row in result
    ]

    response = client.get("/products/")

    assert response.status_code == 200
    assert response.json() == {"Produtos" : dados}


def test_editar_produto_pela_id():
    p = {
        "sku": "BK-M18B-52",
        "nome": "Mountain-500 Black, 52",
        "nomeModelo": "Mountain-500",
        "descricao": "Suitable for any type of riding, on or off-road. Fits any budget. Smooth-shifting with a comfortable ride.",
        "cor": "Black",
        "tamanho": "52",
        "estilo": "U",
        "custo": 294.5797,
        "preco": 539.99,
        "subCategoria": 1
    }

    response = client.put("/products/600", json = p)

    assert response.status_code == 202
    assert response.json() == {"mensagem" : "Produto editado com sucesso"}


    
    response = client.put("/products/5000", json = p)
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Produto com id 5000 nao existe!!"}


def test_deletar_produto_pela_id():
    response = client.delete("/products/607")

    assert response.status_code == 202
    assert response.json() == {"mensagem" : "Produto deletado com sucesso"}

    response = client.delete("/products/5000")
    assert response.status_code == 404
    assert response.json() == {"detail": "Produto com id 5000 nao existe!!"}
# --------------------------------------------------------------------



# ------------------------- Testes Tarefa 02 -------------------------

def test_top10_produtos_mais_vendidos():
    query = db.text(f"""
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
    """)

    result = connection.execute(query)
    dados = [{"Id_Produto" : row[0], "Produto" : row[1], "Vendas_totais" : row[2]} for row in result]

    response = client.get("/sales/top-products/category/1")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == dados


def test_cliente_com_mais_pedidos():
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

    response = client.get("/sales/best-customer/")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == dados


def test_mes_com_mais_venda():
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

    response = client.get("/sales/busiest-month/")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == dados


def test_territorios_com_vendas_acima_da_media():
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

    response = client.get("/sales/top-territories/")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == dados