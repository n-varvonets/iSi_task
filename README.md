# Simple Chat Application

This is a simple chat application built using Django and Django REST Framework.

## Requirements

- Python 3.8+
- Django
- Django REST Framework
- JWT Authentication (Simple JWT)

## Running the application

1. Install the dependencies:

```bash
pip install -r requirements.txt


```
тест кейс, когда добавляешь к несуществбщему треду
или отправляешь смс пользоватлем в тред, которого нет в тредах
![img.png](img.png)
- обработал кейс с отпрвкой смс в несуществующий чат или несуществующем отправителем
- так же нужно обработать создание треда с 2мя темеже участниками
- так же нужно добавить обработку кейса с созданием треда передав два айди одного и того же участника 