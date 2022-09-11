import asyncio
import os
from functools import lru_cache
from time import sleep

import httpx
import database

from datetime import datetime
from add_extractor import UtilsExtractor, AddExtractor
from playhouse.pool import PooledPostgresqlDatabase
from multiprocessing import Pool, Event, Manager

adds_data = []
add = {}
pool = None


@lru_cache(maxsize=32)
async def gather_adds():
    current_page = 1
    is_next_elem_present = True

    async with httpx.AsyncClient() as client:
        while is_next_elem_present:
            response = await client.get(
                f'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{current_page}/c37l1700273?ad=offering',
                follow_redirects=True, timeout=3000)

            adds = AddExtractor(response.text).get_all_adds()
            await asyncio.sleep(3)
            print("current page", current_page)
            print(len(adds))
            for info_container in adds:
                print("info")
                add_extractor = AddExtractor(info_container)
                image = add_extractor.extract_image()
                title = add_extractor.extract_title()
                location = add_extractor.extract_location()
                date_posted = add_extractor.extract_date_posted()
                description = add_extractor.extract_description()
                currency = add_extractor.extract_currency()
                number_of_beds = add_extractor.extract_number_of_beds()

                # convert to date
                if len(date_posted.split("/")) > 1:
                    date_time = datetime.strptime(date_posted, '%d/%m/%Y').date()
                else:
                    date_time = datetime.today().date()
                print(image)
                print(title)
                print(location)
                print(date_posted)
                print(description)
                print(currency)
                print(number_of_beds)

                add = dict(
                    image=image,
                    title=title,
                    location=location,
                    date_posted=date_time,
                    description=description,
                    currency=currency,
                    number_of_beds=number_of_beds)
                adds_data.append(add)

            is_next_elem_present = UtilsExtractor(response.text).is_next_element_present()
            current_page += 1

    return adds_data


async def get_adds():
    adds = await gather_adds()
    return adds


def set_global_db_conn(event):
    global pool
    print(f'PID {os.getpid()} initializing pool.....')
    pool = PooledPostgresqlDatabase('db', user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'),
                                    host=os.getenv('DB_LOCALHOST'), port=5432, max_connections=100,
                                    stale_timeout=300)
    event.wait()


def insert_add(add, event):
    with pool as p:
        p.create_tables([database.Add])
        add, created = database.Add.get_or_create(
            image=add['image'],
            title=add['title'],
            location=add['location'],
            date_posted=add['date_posted'],
            description=add['description'],
            currency=add['currency'],
            number_of_beds=add['number_of_beds']
        )
        print(add.id)


async def process_adds():
    adds = await get_adds()
    with Manager() as manager:
        event = manager.Event()
        with Pool(initializer=set_global_db_conn, initargs=[event]) as pool:
            adds_with_event = [(add, event) for add in adds]

            result = pool.starmap_async(insert_add, adds_with_event)
            # wait a moment
            # start all issued tasks
            print('Setting event.', flush=True)
            print('Main process blocking...')
            sleep(5)
            event.set()
            # wait for all tasks to finish
            result.wait()
            print('All done.', flush=True)


if __name__ == '__main__':
    asyncio.run(process_adds())
