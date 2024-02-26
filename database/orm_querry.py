from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import homework, combo, usertable
from LOGGING.LoggerConfig import logger

######################################################################################################
async def orm_add_user(session: AsyncSession, data:dict):
    try:
        query = select(usertable).where(usertable.chat_id==data['chat_id'])
        result = await session.execute(query)
        result.scalars().first().chat_id
        query = update(usertable).where(usertable.chat_id == data['chat_id']).values(data)
        await session.execute(query)
        await session.commit() 
        logger.info(f'Пользователь успешно {data['username']} сменил свои данные!')
    except:
        table = usertable(
            username = data['username'],
            chat_id = data['chat_id'], 
            group = data['group'],
            login = data['login'],
            password = data['password'],
            key = data['key']
        )
        logger.info(f'Пользователь {data['username']} успешно прошел регистрацию!')
        session.add(table)
        await session.commit()
   
######################################################################################################


async def orm_get_user_group(session: AsyncSession, id):
    query = select(usertable).where(usertable.chat_id == id).order_by(usertable.id.desc()).limit(1)

    result = await session.execute(query)
    scl = result.scalars().first()

    group = scl.group
    return group

async def orm_get_group_users_list(session: AsyncSession, group):
    query = select(usertable.chat_id).where(usertable.group==group)

    result = await session.execute(query)
    scl = result.fetchall()
    
    chat_ids = [item[0] for item in scl]
    return chat_ids

async def orm_get_users_ids(session: AsyncSession):
    query = select(usertable.chat_id)

    result = await session.execute(query)
    scl = result.fetchall()
    
    chat_ids = [item[0] for item in scl]
    return chat_ids

async def orm_get_identifiers(session: AsyncSession, id):
    querry = select(usertable).where(usertable.chat_id == id).order_by(usertable.id.desc()).limit(1)
    result = await session.execute(querry)
    scl = result.scalars().first()

    login = scl.login
    password = scl.password
    
    key = scl.key
    
    return login, password, key
######################################################################################################

async def orm_add_combo(session: AsyncSession , data: dict):
    table = combo(
        compound = data['compound'],
        price = data['price']
    )
    session.add(table)
    await session.commit()

async def orm_get_combo_comp(session: AsyncSession):
    querry = select(combo.compound).order_by(combo.id.desc()).limit(1)
    querry2 = select(combo.price).order_by(combo.id.desc()).limit(1)

    result = await session.execute(querry)
    result2 = await session.execute(querry2)

    compound = result.scalars().first()
    price = result2.scalars().first()

    return compound, price

######################################################################################################

async def orm_add_homework(session: AsyncSession, data: dict):
    obj = homework(
        subject = data['subject'],
        task = data['task'],
        group = data['group'],
        ContentType = data['Ctype']
    )
    session.add(obj)
    await session.commit()


async def orm_get_homework(session: AsyncSession, subject, group):
    querry = select(homework).where((homework.subject == subject) & (homework.group == group)).order_by(homework.id.desc()).limit(1)

    result = await session.execute(querry)
    scl = result.scalars().first()

    task = scl.task
    ContentType = scl.ContentType
    return task, ContentType
    
######################################################################################################