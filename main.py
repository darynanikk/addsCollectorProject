import asyncio
import httpx
import database
from add_extractor import AddExtractor, UtilsExtractor
from datetime import datetime


async def main():
    current_page = 1
    is_next_elem_present = True

    async with httpx.AsyncClient() as client:
        while is_next_elem_present:
            response = await client.get(
                f'https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{current_page}/c37l1700273?ad=offering',
                follow_redirects=True, timeout=3000)

            print(response.status_code)
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
                with database.pg_db as db:
                    db.create_tables([database.Add])
                    add, created = database.Add.get_or_create(
                        image=image,
                        title=title,
                        location=location,
                        date_posted=date_time,
                        description=description,
                        currency=currency,
                        number_of_beds=number_of_beds
                    )
                    print(add.id)

            current_page += 1
            is_next_elem_present = UtilsExtractor(response.text).is_next_element_present()


if __name__ == '__main__':
    asyncio.run(main())
