from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import csv
import os
from ast import literal_eval


def new_status(eps, total):
    try:
        if (eps / total) * 100 > 90:
            return 'star'
        elif (eps / total) * 100 > 50:
            return 'main cast'
        elif eps > 1:
            return 'guest'
        else:
            return 'cameo/extra'
    except TypeError:
        return 'cameo/extra'


class Actor:
    def __init__(self, link, show, role, eps, total):
        self.link = link
        self.roles = {show: role}
        self.episodes = {show: eps}
        self.status = {show: new_status(eps, total)}

    def add_role(self, show, role, eps, total):
        self.roles.update({show: role})
        self.episodes.update({show: eps})
        self.status.update({show: new_status(eps, total)})


def new_completed():
    if os.path.exists('csv_file.csv'):
        os.remove('csv_file.csv')
    with open('completed_titles.txt', 'w') as completed:
        completed.writelines("Completed titles by LAextra:")
    with open('blacklist.txt', 'w') as completed:
        completed.writelines("Titles shot outside the US:")


def write_setup(reset=False):
    completed_titles = []
    blacklist = []
    if reset:
        new_completed()
    else:
        try:
            with open('completed_titles.txt', 'r') as completed:
                completed_titles = completed.readlines()
                if len(completed_titles) > 1:
                    completed_titles = [i.strip() for i in completed_titles[1:]]
                else:
                    completed_titles.clear()
            with open('blacklist.txt', 'r') as blacktitles:
                blacklist = blacktitles.readlines()
                if len(blacklist) > 1:
                    blacklist = [i.strip() for i in blacklist[1:]]
                else:
                    blacklist.clear()
        except FileNotFoundError:
            new_completed()
    return completed_titles, blacklist


def add_to_blacklist(title):
    with open('blacklist.txt', 'a') as blacktitles:
        blacktitles.write('\n' + title)


def new_csv(actors, title, stop):
    fieldnames = ['name', 'weblink', 'shows', 'roles', 'episodes', 'status']
    overwrite_actors = []
    with open('new_file.csv', 'w', newline='') as new_file:
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        try:
            with open('csv_file.csv', 'r') as old_file:
                csv_reader = csv.DictReader(old_file)
                for line in csv_reader:
                    if line['name'] in actors:
                        name = line['name']
                        overwrite_actors.append(name)
                        link = line['weblink']
                        shows = int(line['shows']) + 1
                        roles = literal_eval(line['roles'])
                        episodes = literal_eval(line['episodes'])
                        status = literal_eval(line['status'])
                        roles.update(actors[name].roles)
                        episodes.update(actors[name].episodes)
                        status.update(actors[name].status)
                        csv_writer.writerow({
                            'name': name,
                            'weblink': link,
                            'shows': shows,
                            'roles': roles,
                            'episodes': episodes,
                            'status': status
                        })
                    else:
                        csv_writer.writerow(line)
        except FileNotFoundError:
            pass
        for actor in actors:
            if actor not in overwrite_actors:
                csv_writer.writerow({
                    'name': actor,
                    'weblink': actors[actor].link,
                    'shows': len(actors[actor].roles),
                    'roles': actors[actor].roles,
                    'episodes': actors[actor].episodes,
                    'status': actors[actor].status
                })
    with open('completed_titles.txt', 'a') as completed:
        completed.write('\n' + title)
    try:
        os.replace('new_file.csv', 'csv_file.csv')
    except FileNotFoundError:
        os.rename('new_file.csv', 'csv_file.csv')
    if stop:
        breakpoint()


def main(completed_titles, blacklist, stop=False):
    PATH = "C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    start_url = "https://www.imdb.com/search/title/?genres=comedy&explore=title_type,genres&title_type=tvSeries&ref_=adv_explore_rhs"
    driver.get(start_url)
    titles = []
    ids_ = []
    titles_dict = {}
    for i in range(3):
        load_titles = []
        while len(load_titles) < 50:
            load_titles = driver.find_elements_by_xpath("//a[contains(@href, '?ref_=adv_li_tt')]")
        titles.extend(j.text for j in load_titles)
        ids_.extend(j.get_attribute("href") for j in load_titles)
        if i < 2:
            driver.find_element_by_class_name('next-page').click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "styleguide-v2")))
    if any(titles.count(i) > 1 for i in titles):
        for title in set([i for i in titles if titles.count(i) > 1]):
            for e in range(2, titles.count(title) + 1):
                ind = [i for i, n in enumerate(titles) if n == title][e - 1]
                titles[ind] = f'{title} ({e})'
    titles_dict.update({title: id_ for title, id_ in zip(titles, ids_)})
    for title in completed_titles + blacklist:
        if title in titles_dict:
            titles_dict.pop(title)
    for title in titles_dict:
        actor_dict = {}
        driver.get(titles_dict[title])
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'country_of_origin')]")))
        except TimeoutException:
            blacklist.append(title)
            add_to_blacklist(title)
            continue
        origin = driver.find_element_by_xpath("//a[contains(@href, 'country_of_origin')]").text
        if origin != 'USA':
            blacklist.append(title)
            add_to_blacklist(title)
            continue
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'add_episode')))
        sub_text = driver.find_elements_by_class_name('bp_sub_heading')
        if len(sub_text) == 1:
            total_episodes = int(sub_text[0].text.split(' ')[0])
        else:
            total_episodes = int(sub_text[1].text.split(' ')[0])
        print(f'{title}, eps: {total_episodes}')
        driver.find_element_by_xpath("//a[contains(@href, 'fullcredits')]").click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cast_list')))
        cast_list = driver.find_element_by_class_name('cast_list')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'add_episode')))
        rows = cast_list.find_elements(By.TAG_NAME, "tr")[1::2]
        for row in rows:
            name = row.find_elements(By.TAG_NAME, "td")[1].text
            if name in actor_dict and title in actor_dict[name].roles:
                continue
            link = row.find_element(By.XPATH, ".//a[contains(@href, '/name/')]").get_attribute('href')
            try:
                character = row.find_element(By.XPATH, ".//a[contains(@href, '/characters/')]").text
            except NoSuchElementException:
                character = 'N/A'
            episodes = row.find_element(By.XPATH, ".//a[contains(@href, '#')]").text
            try:
                episodes = int(episodes.split(' ')[0])
            except ValueError:
                episodes = episodes.split(' ')[0]
            if name in actor_dict:
                actor_dict[name].add_role(title, character, episodes, total_episodes)
            else:
                actor_dict.update({name: Actor(link, title, character, episodes, total_episodes)})
            print(name + ', ' + actor_dict[name].roles[title] + ', ' + actor_dict[name].status[title])
        new_csv(actor_dict, title, stop)
    print('Finished!')
    driver.quit()


if __name__ == '__main__':
    completed_titles, blacklist = write_setup() # pass True to write_setup to reset and delete files
    main(completed_titles, blacklist) # pass True as the third value to main to add breakpoints after each title
