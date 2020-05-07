from telegram.ext import (Updater, InlineQueryHandler, CommandHandler, CallbackContext, MessageHandler, Filters)
import telegram
import requests
import re
import json
from datetime import date,datetime
import logging
from functools import wraps
import numbers
import geocoder
import pyshorteners
from pyshorteners import Shorteners

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)
today = date.today()
regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

r = requests.get('https://api.covid19india.org/data.json')
j = r.json()

r = requests.get('https://api.covid19india.org/v2/state_district_wise.json')
dist_data = r.json()

rCountry = requests.get('http://corona-api.com/countries')
jCountry = rCountry.json()

contents = requests.get("https://api.covid19api.com/summary").json()
totalContent = requests.get("https://api.covid19api.com/world/total").json()

continent = requests.get('https://corona.lmao.ninja/v2/continents?yesterday=true&sort')
continent_v = continent.json()

rUS = requests.get('https://covidtracking.com/api/states/info')
jstates = rUS.json()

rUS_states = requests.get('https://covidtracking.com/api/states')
states_us = rUS_states.json()

APIKey_LQ = ""
API_key_M = ""

def get_count_world():
    
    ijson = contents["Global"]
    TotalConfirmed = str(totalContent["TotalConfirmed"])
    NewConfirmed = str(ijson["NewConfirmed"])
    NewDeaths = str(ijson["NewDeaths"])
    TotalDeaths = str(totalContent["TotalDeaths"])
    TotalRecovered = str(totalContent["TotalRecovered"])
    NewRecovered = str(ijson["NewRecovered"])
    return TotalConfirmed,NewConfirmed,NewDeaths,TotalDeaths,TotalRecovered,NewRecovered

def world(update, context):
    content = get_count_world()
    print (content)
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="The total number of *infected* people in the world are: *"+content[0]+"* \
    \nThe number of *new confirmed* cases people in the world are: *"+content[1]+"* \
    \nThe number of *new deaths* in the world are: *"+content[2]+"* \
    \nThe *total* number of *dead* people in the world are: *"+content[3]+"*\
    \nThe number of people who have *recovered* in the world are: *"+content[4]+"* \
    \nThe number of *newly recovered* people in the world are: *"+content[5]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    print("This User checked world :"+update.message.from_user.first_name)
    logger.info("World handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)
    
def new_count_India():

    for each in j["statewise"]:
        if str(each["state"]) == "Total":
           confirmed = str(each["confirmed"]) 
           deaths = str(each["deaths"]) 
           recovered = str(each["recovered"])
           deltaconfirmed = str(each["deltaconfirmed"])
           lastupdatedtime = str(each["lastupdatedtime"])
    return confirmed,deaths,recovered,deltaconfirmed,lastupdatedtime

def india(update, context):
    content = new_count_India()
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="The number of *infected* people in *India* are: *"+content[0]+"*\
    \n The number of *deaths* are: *"+content[1]+"*\
    \n The number of *recovered* people are: *"+content[2]+"*\
    \n The number of *newcases* as of today are: *"+content[3]+"*\
    \n This data was last updated at : *"+content[4]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    print("This User checked India: "+update.message.from_user.first_name)
    logger.info("India handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def state_new_count_India(var):

    for each in j["statewise"]:
        if str(each["statecode"]) == var:
           confirmed = str(each["confirmed"]) 
           deaths = str(each["deaths"]) 
           recovered = str(each["recovered"])
           deltaconfirmed = str(each["deltaconfirmed"])
           lastupdatedtime = str(each["lastupdatedtime"])
           stateName = str(each["state"])
    return confirmed,deaths,recovered,deltaconfirmed,lastupdatedtime,stateName

def indianstate(update, context):
    state_code = ' '.join(context.args).upper()
    print(state_code)
    if (state_code.isdigit()):
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a statecode, Ex: '/state KA'",parse_mode=telegram.ParseMode.MARKDOWN)
    elif state_code == "":
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a statecode, Ex: '/state KA'",parse_mode=telegram.ParseMode.MARKDOWN)
    elif(regex.search(state_code)) == None:
        content_k = state_new_count_India(state_code)
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text="The number of *infected* people in *"+content_k[5]+"* are: *"+content_k[0]+"*\
        \n The number of *deaths* in this state are: *"+content_k[1]+"*\
        \n The number of *cured* people in this state are: *"+content_k[2]+"*\
        \n The number of *newcases* as of today in this state are: *"+content_k[3]+"*\
        \n This data was last updated at : *"+content_k[4]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a statecode correctly , Ex: '/state KA",parse_mode=telegram.ParseMode.MARKDOWN)   
    logger.info("State handler used ", update.message.chat.id, update.message.from_user.first_name)
    print("This User checked "+ content_k[5] +":"+update.message.from_user.first_name)

def indian_state_code(update, context):
    state = []
    code = []
    for each in j['statewise']:    
        state.append(each["state"])
        code.append(each["statecode"])
    
    StateName_StateCode = ' \n'.join(["For "+ str(a) +" use code "+ b for a,b in zip(state,code)])
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="*"+StateName_StateCode+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    logger.info("State code handler used ", update.message.chat.id, update.message.from_user.first_name)   

def country_code(update, context):
    var = ' '.join(context.args)
    print(var)
    if var == "":
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a Letter to list the countries , Ex: '/countrycode N",parse_mode=telegram.ParseMode.MARKDOWN)
    elif (var.isdigit()):
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a Letter to list the countries , Ex: '/countrycode N",parse_mode=telegram.ParseMode.MARKDOWN)
    elif(regex.search(var)) == None:
        letter = var.capitalize()
        print(letter)
        
        #print (j['statewise'])
        """ for each in jCountry['data']:
            countryName = str(each["name"]) 
            if countryName.startswith(letter):
                countryCode = str(each["code"])
        """
        country = []
        country_code = []
        for each in jCountry['data']:
            countryName = str(each["name"])
            if countryName.startswith(letter):
                country.append(each["name"])
                country_code.append(each["code"]) 
            
        countryName_countryCode = ' \n'.join([str(a) +" use code : "+ b for a,b in zip(country,country_code)])
        chat_id = update.message.chat_id
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=chat_id, text="List of Countries starting with letter *"+letter+"* :\n*"+countryName_countryCode+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a Letter to list the countries , Ex: '/countrycode N",parse_mode=telegram.ParseMode.MARKDOWN)
    logger.info("Country code handler used ", update.message.chat.id, update.message.from_user.first_name)

def countryWiseStatsCollect(var):
    print(str(var).upper())
    for each in jCountry["data"]:
        if str(each["code"]) == str(var).upper():
            confirmed = str(each["latest_data"]["confirmed"])
            deaths = str(each["latest_data"]["deaths"]) 
            recovered = str(each["latest_data"]["recovered"])
            populationHere = str(each["population"])
            lastupdatedtime = str(each["updated_at"])
            countryName = str(each["name"])
            new_case = str(each["today"]["confirmed"])
    return confirmed,deaths,recovered,populationHere,lastupdatedtime,countryName,new_case

def countryWiseData(update, context):
    country_code = ' '.join(context.args)
    letter = country_code.capitalize()
    print(country_code)
    if (country_code.isdigit()):
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a country code, Ex:'/country NL'",parse_mode=telegram.ParseMode.MARKDOWN)
    elif country_code == "":
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a country code, Ex:'/country NL'",parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        content_k = countryWiseStatsCollect(letter)
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text="The number of *infected* people in *"+content_k[5]+"* are: *"+content_k[0]+"*\
        \nThe number of *new cases* for today in this country are: *"+content_k[6]+"*\
        \nThe number of *deaths* in this country are: *"+content_k[1]+"*\
        \nThe number of *cured* people in this country are: *"+content_k[2]+"*\
        \nThe *population* as of today in this country are: *"+content_k[3]+"*\
        \nThis data was last updated at : *"+content_k[4]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
        print("This User checked "+ content_k[5] +":"+update.message.from_user.first_name)
        logger.info("Country handler used ", update.message.chat.id, update.message.from_user.first_name)
        captureID(update)

def topC(update, context):
    var = ' '.join(context.args)
    #res = isinstance(var, str)
    country = []
    country_code = []
    deaths = []
    confirmed =[]
    countryN = []
    confirmedcountry = []
    confirmedN = []
    if var == "":
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a number after the handler to get the results, Ex: '/topC 10",parse_mode=telegram.ParseMode.MARKDOWN)
    elif ((var>='a' and var<= 'z') or (var>='A' and var<='Z')):
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a number after the handler to get results, Ex: '/topC 10",parse_mode=telegram.ParseMode.MARKDOWN)
    elif ((var >= '50')):
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a number below 50 with the handler to get results, Ex: '/topD 10",parse_mode=telegram.ParseMode.MARKDOWN)
    elif(regex.search(var)) == None:
        for each in jCountry["data"]:
            confirmed.append(each["latest_data"]["confirmed"])
            country.append(str(each["name"]))
            country_code.append(str(each["code"]))
            deaths.append(str(each["latest_data"]["deaths"]))
        #print(confirmed)
        confirmed.sort(reverse = True)
        top = confirmed[0:int(var)]
        #print("This is sorted:",confirmed)
        #print(top)
        j=0
        for i in top:
            for each in jCountry["data"]:
                confirmedN = each["latest_data"]["confirmed"]
                if (i == confirmedN):
                    confirmedcountry.append(str(each["latest_data"]["confirmed"]))
                    countryN.append("No:"+str(j+1)+">> "+str(each["name"]))
                    j += 1
                    
        countryName_confirmed = ' \n'.join(["*"+str(a)+"*"+" has *"+ b +"* confirmed cases" for a,b in zip(countryN,confirmedcountry)])
    else:
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a number below 50 with the handler to get results, Ex: '/topD 10",parse_mode=telegram.ParseMode.MARKDOWN)  
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="The *Top "+var+"* countries with max confirmed cases of Covid-19 are : \
    \n"+countryName_confirmed+"",parse_mode=telegram.ParseMode.MARKDOWN)
    print("This User checked TopC: "+update.message.from_user.first_name)
    logger.info("TopC handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def topD(update, context):
    var = ' '.join(context.args)
    #res = isinstance(var, str)
    country = []
    deaths = []
    countryN = []
    deathCountry = []
    if var == "":
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a number after the handler to get the results, Ex: '/topD 10",parse_mode=telegram.ParseMode.MARKDOWN)
    elif ((var>='a' and var<= 'z') or (var>='A' and var<='Z')):
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a number after the handler to get results, Ex: '/topD 10",parse_mode=telegram.ParseMode.MARKDOWN)
    elif ((var >= '50')):
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a number below 50 with the handler to get results, Ex: '/topD 10",parse_mode=telegram.ParseMode.MARKDOWN)
    elif(regex.search(var)) == None:
        for each in jCountry["data"]:
            country.append(str(each["name"]))
            deaths.append(each["latest_data"]["deaths"])
        #print(confirmed)
        deaths.sort(reverse = True)
        top = deaths[0:int(var)]
        #print("This is sorted:",confirmed)
        #print(top)
        j=0
        for i in top:
            for each in jCountry["data"]:
                deathN = each["latest_data"]["deaths"]
                if (i == deathN):
                    deathCountry.append(str(each["latest_data"]["deaths"]))
                    countryN.append("No:"+str(j+1)+">> "+str(each["name"]))
                    j += 1

        countryName_death = ' \n'.join(["*"+str(a)+"*"+" has *"+ b +"* deaths from Covid-19" for a,b in zip(countryN,deathCountry)])
    else:
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a number below 50 with the handler to get results, Ex: '/topD 10",parse_mode=telegram.ParseMode.MARKDOWN)
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="The *Top "+var+"* countries with max death cases are : \
    \n"+countryName_death+"",parse_mode=telegram.ParseMode.MARKDOWN)
    print("This User checked TopD: "+update.message.from_user.first_name)
    logger.info("TopD handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def help(update,context):
    logger.info("help handler used ", update.message.chat.id, update.message.from_user.first_name)
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=update.message.chat_id, text= "\
    \n \
    \n<b><u>Commands:</u></b> \n \
    \n/india - Fetch stats of India \n\
    \n/statecode - Fetch statewise code \n\
    \n/state statecode - Fetch stats per state,\
    Now for karnataka use '/state KA' without the single quotes \n \
    \n/districtwise - Fetch stats district wise of a particular state using the state code \n\
    \n/world - Fetch stats for the entire world \n\
    \n/countrycode - Fetch country codes ,\n\
    To show all country names with starting letter I and thier respective code  use '/countrycode I' \n \
    \n/country countrycode - Fetch country wise stats,\n \
    Now for showing stats of Netherlands use '/country NL' \n\
    \n/topC number - Fetch top countries with highest confirmed covid-19 cases, \n\
    Now to show Top 10 countries use '/topC 10' without the single quotes \n\
    \n/topD number - Fetch top countries with highest death due to covid-19, \n\
    Now to show Top 10 countries use '/topD 10' without the single quotes \n\
    \n \
    \nYou can now <b>share your current location</b> and get the stats,\
    \nIf you share your location inside <b>India</b> then you get <b>statewise</b> stats, \n\
    \nIf you share your location inside <b>USA</b> then you get <b>statewise</b> stats, \n\
    \nIf you share any location outside India and USA then you get that specific <b>country</b> stats, \n\
    \n<b>Just point the pin on the map and share it</b> \n \
    \n\
    \n/ListUSAStates - Lists all 56 state codes \n\
    To show all state names with starting letter N and thier respective code  use '/ListUSAStates N' \n \
    \n/USAState statecode - Fetch stats per state,\n\
    Now for NewYork use '/USAState NY' without the single quotes \n \
    \n/asia - Fetch stats of Asia\n \
    \n/africa - Fetch stats of Africa\n \
    \n/europe - Fetch stats of Europe\n \
    \n/australia - Fetch stats of Australia\n \
    \n/northamerica - Fetch stats of North America\n \
    \n/southamerica - Fetch stats of South America\n \
    \n /official_TC to see official Telegram channels of other countries \
    ",parse_mode=telegram.ParseMode.HTML,disable_web_page_preview=True)
    print(update.message.from_user.username)
    captureID(update)

def start(update,context):
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=update.message.chat.id, text="<b>Welcome to The Covid-19 Tracker Bot! 🦠</b> \
    \n \
    \n<b><u>You can use these Commands:</u></b> \n \
    \n/india - Fetch stats of India \n\
    \n/statecode - Fetch statewise code \n\
    \n/state statecode - Fetch stats per state,\
    Now for karnataka use '/state KA' without the single quotes \n \
    \n/districtwise - Fetch stats district wise of a particular state using the state code \n\
    \n/world - Fetch stats for the entire world \n\
    \n/countrycode - Fetch country codes ,\n\
    To show all country names with starting letter I and thier respective code  use '/countrycode I' \n \
    \n/country countrycode - Fetch country wise stats,\n \
    Now for showing stats of Netherlands use '/country NL' \n\
    \n/topC number - Fetch top countries with highest confirmed covid-19 cases, \n\
    Now to show Top 10 countries use '/topC 10' without the single quotes \n\
    \n/topD number - Fetch top countries with highest death due to covid-19, \n\
    Now to show Top 10 countries use '/topD 10' without the single quotes \n\
    \n \
    \nYou can now <b>share your current location</b> and get the stats,\
    \nIf you share your location inside <b>India</b> then you get <b>statewise</b> stats, \n\
    \nIf you share your location inside <b>USA</b> then you get <b>statewise</b> stats, \n\
    \nIf you share any location outside India and USA then you get that specific <b>country</b> stats, \n\
    \n<b>Just point the pin on the map and share it</b> \n \
    \n \
    \n<b>Fetch Stats for USA</b>\
    \n/ListUSAStates - Lists all 56 state codes \n\
    To show all state names with starting letter N and thier respective code  use '/ListUSAStates N' \n \
    \n/USAState statecode - Fetch stats per state,\n\
    Now for NewYork use '/USAState NY' without the single quotes \n \
    \n\
    \n<b>Fetch stats Continent wise</b> \
    \n/asia - Fetch stats of Asia\n \
    \n/africa - Fetch stats of Africa\n \
    \n/europe - Fetch stats of Europe\n \
    \n/australia - Fetch stats of Australia\n \
    \n/northamerica - Fetch stats of North America\n \
    \n/southamerica - Fetch stats of South America\n \
    \n Data from - https://www.covid19india.org/  \
    \n             https://about-corona.net/documentation \
    \n \
    \n Official Indian Govt. Telegram Channel: @MyGovCoronaNewsdesk \
    \n /official_TC to see official Telegram channels of other countries \
    \n \
    \n Remember to use /help anytime to see these commands \
    \n Stay Home, Stay Safe! 🏡"+ update.message.from_user.first_name
    ,parse_mode=telegram.ParseMode.HTML,disable_web_page_preview=True)
    print(update.message.from_user.username)
    print(update.message.from_user.first_name)
    print(update.message.chat.id)
    captureID(update)
    logger.info("Start handler used ", update.message.chat.id, update.message.from_user.first_name)

def captureID(update):
    f= open("userID.txt","w+")
    f= open("guru99.txt", "a+")
    f.write("\nUser is %d\r" % (update.message.chat.id)+": "+(update.message.from_user.first_name))

def officialTelegramChannels(update,context):
    logger.info("officialTelegramChannels handler used ", update.message.chat.id, update.message.from_user.first_name)
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=update.message.chat_id, text= """\
    If you're looking for official news about the Novel Coronavirus and COVID-19, here are some examples of verified Telegram channels from health ministries around the world.\

    🇨🇺 <a href="https://t.me/MINSAPCuba">Cuba</a>
    🇬🇪 <a href="https://t.me/StopCoVge">Georgia</a>
    🇩🇪 <a href="https://t.me/Corona_Infokanal_BMG">Germany</a>
    🇭🇰 <a href="http://t.me/HKFIGHTCOVID19">Hong Kong</a>
    🇮🇳 <a href="https://t.me/MyGovCoronaNewsdesk">India</a>
    🇮🇹 <a href="https://t.me/MinisteroSalute">Italy</a>
    🇮🇱 <a href="https://t.me/MOHreport">Israel</a>
    🇰🇿 <a href="https://t.me/coronavirus2020_kz">Kazakhstan</a>
    🇰🇬 <a href="https://t.me/RshKRCOV">Kyrgyzstan</a>
    🇲🇾 <a href="https://t.me/cprckkm">Malaysia</a>
    🇳🇬 <a href="http://t.me/ncdcgov">Nigeria</a>
    🇷🇺 <a href="https://t.me/stopcoronavirusrussia">Russia</a>
    🇸🇦 <a href="https://t.me/LiveWellMOH">Saudi Arabia</a>
    🇸🇬 <a href="https://t.me/govsg">Singapore</a>
    🇪🇸 <a href="https://t.me/sanidadgob">Spain</a>
    🇹🇬 <a href="http://t.me/GouvTG">Togo</a>
    🇺🇦 <a href="https://t.me/COVID19_Ukraine">Ukraine</a>
    🇺🇿 <a href="https://t.me/koronavirusinfouz">Uzbekistan</a>
    """,parse_mode=telegram.ParseMode.HTML,disable_web_page_preview=True)
    print(update.message.from_user.username)
    logger.info("officialTelegramChannels handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def getLocation(update,context):
    message = None
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    current_lat = str(message.location.latitude)
    current_lon = str(message.location.longitude)
    print(current_lat)
    print(current_lon)
    
    contents = requests.get("https://locationiq.com/v1/reverse.php?key="+APIKey_LQ+"&lat="+current_lat+"&lon="+current_lon+"&format=json").json()
    countryName = contents["address"]["country"]
    country = contents["address"]["country_code"]
    if country == "in":
        state = contents["address"]["state"]
        for each in j["statewise"]:
            if str(each["state"]) == state:
                confirmed = str(each["confirmed"]) 
                deaths = str(each["deaths"]) 
                recovered = str(each["recovered"])
                deltaconfirmed = str(each["deltaconfirmed"])
                lastupdatedtime = str(each["lastupdatedtime"])
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are currently living in *"+countryName+"* \
        \nThe Pin on the map is in *"+state+"* \
        \nThe number of *infected* people in *"+state+"* are: *"+confirmed+"*\
        \nThe number of *deaths* in this state are: *"+deaths+"*\
        \nThe number of *cured* people in this state are: *"+recovered+"*\
        \nThe number of *newcases* as of today in this state are: *"+deltaconfirmed+"*\
        \nThis data was last updated at : *"+lastupdatedtime+"*",parse_mode=telegram.ParseMode.MARKDOWN)
        getLocation1(update,context,current_lat,current_lon,lastupdatedtime)
        links(context,update,current_lat,current_lon)
    elif country == "us":
        state = contents["address"]["state"]
        print(state)
        for each in jstates:
            if str(each["name"]) == state:
                value = us_statewise_stats(str(each["state"]))
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are currently located in or the Map location shared is in *"+state+"*: *"+value[0]+"*\
        \nThe number of *deaths* in this state are: *"+value[1]+"*\
        \nThe number of *recovered* people in this state are: *"+value[2]+"*\
        \nThis data was last updated at : *2020/"+value[3]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
        links(context,update,current_lat,current_lon)
    else :#country = url['country_code']
        content_k = countryWiseStatsCollect(country)
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are currently located in or the Map location shared is in *"+content_k[5]+"* \
        \nThe number of *infected* people in this country are: *"+content_k[0]+"*\
        \nThe number of *deaths* in this country are: *"+content_k[1]+"*\
        \nThe number of *cured* people in this country are: *"+content_k[2]+"*\
        \nThe *population* as of today in this country are: *"+content_k[3]+"*\
        \nThis data was last updated at : *"+content_k[4]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
        print("This User checked "+ content_k[5] +":"+update.message.from_user.first_name)
    
    logger.info("Location handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)
    #context.bot.send_message(chat_id=update.message.chat_id, text="Would you mind sharing your location and contact with me?",reply_markup=reply_markup)

def links(context,update,current_lat,current_lon):
    s = pyshorteners.Shortener(Shorteners.TINYURL)
    response = s.short("https://www.google.com/maps/search/food+shelters/@"+current_lat+","+current_lon+",13z")
    context.bot.send_message(chat_id=update.effective_chat.id, text="*Below you can find the food shelters in this area*\n"+response,parse_mode=telegram.ParseMode.MARKDOWN)
    s = pyshorteners.Shortener(Shorteners.TINYURL)
    response1 = s.short("https://www.google.com/maps/search/night+shelters/@"+current_lat+","+current_lon+",12z")
    context.bot.send_message(chat_id=update.effective_chat.id, text="*Below you can find the Night shelters in this area*\n"+response1,parse_mode=telegram.ParseMode.MARKDOWN)

def ask_state_for_districtwise_msg():
    return 'Which state\'s district count do you want?'

def get_district_msg(state_name):
    #dist_data = get_data('data_district.json')
    #print(dist_data)
    state_data = []
    for s in dist_data:
        if s['statecode'].lower() == state_name.lower().strip():
            state_name = s['state']
            state_data = s['districtData']
            break
    districtwise_msg = "No data found for State {state_name}".format(state_name=state_name)
    if state_data != []:
        state_data = sorted(state_data, key = lambda i: i['confirmed'],reverse=True)
        districtwise_msg = "District-wise confirmed cases, new cases, recovered cases and death cases till now in <b>{state_name}</b> \n\n<b>NC</b> = New cases \n<b>TR</b> = Total recovered cases\n<b>TD</b> = Total death cases \n".format(state_name=state_name)
        for district in state_data:
            formatted_district_data = "\n{confirmed:4} : <b>{district_name}</b>  NC:{delta_confirmed} TR:{recovered} TD:{death}".format(confirmed=district['confirmed'], delta_confirmed=get_delta_msg(district), district_name= district['district'], recovered=get_msg_r(district), death=get_msg_d(district))
            districtwise_msg += formatted_district_data
        districtwise_msg += "\n\n Data last updated at " + get_lastupdated_msg()
    #print(districtwise_msg)
    return districtwise_msg

def get_delta_msg(district):
    delta_msg = ""
    if district['delta']['confirmed'] != 0:
        delta_msg += "(+{delta_count})".format(delta_count=district['delta']['confirmed'])
    elif district['delta']['confirmed'] == 0:
        delta_msg += "0"
    return delta_msg

def get_msg_r(district):
    msg_r = ""
    if district['recovered'] != 0:
        msg_r += "(+{count})".format(count=district['recovered'])
    elif district['recovered'] == 0:
        msg_r += "0"
    return msg_r

def get_msg_d(district):
    msg_d = ""
    if district['deceased'] != 0:
        msg_d += "(+{count})".format(count=district['deceased'])
    elif district['deceased'] == 0:
        msg_d += "0"
    return msg_d

def get_lastupdated_msg():
    msg_lastupdated = j['statewise'][0]['lastupdatedtime']
    print (msg_lastupdated)
    return msg_lastupdated

def districtwise(update: telegram.Update, context: CallbackContext):
    message = ask_state_for_districtwise_msg()
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=telegram.ForceReply(),
    )
    logger.info("Districtwise handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def handle_message(update: telegram.Update, context: CallbackContext):
    if update.message.reply_to_message:
        if (update.message.reply_to_message.text== ask_state_for_districtwise_msg()):
            message = get_district_msg(update.message.text)
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.HTML
    )    

def getLocation1(update, context, var, var1, time_u):
    """ message = None
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    current_lat = str(message.location.latitude)
    current_lon = str(message.location.longitude)
    print(current_lat)
    print(current_lon)  """
    current_lat = var
    current_lon = var1
    last_updated_time = time_u
    
    contents = requests.get("http://apis.mapmyindia.com/advancedmaps/v1/"+API_key_M+"/rev_geocode?lat="+current_lat+"&lng="+current_lon+"&format=json").json()
    print(contents)
    for each in contents['results']:
        stateName = str(each["state"])
        district = str(each["district"])
    dist = str((district.replace("District","")).strip())
    print(dist)
    if dist == "Mysore":
        dist = str((dist.replace("Mysore","Mysuru")).strip())
    elif dist =="Tumkur":
        dist = str((dist.replace("Tumkur","Tumakuru")).strip())
    elif dist=="Bellary":
        dist = str((dist.replace("Bellary","Ballari")).strip())
    elif dist=="Belgaum":
        dist = str((dist.replace("Belgaum","Belagavi")).strip())
    elif dist=="Bagalkot":
        dist = str((dist.replace("Bagalkot","Bagalkote")).strip())
    elif dist=="Gulbarga":
        dist = str((dist.replace("Gulbarga","Kalaburagi")).strip())
    
    print(dist)
    rd = requests.get('https://api.covid19india.org/state_district_wise.json')
    rdj = rd.json()
    state = rdj[stateName]
    try:
        confirmed_d = str(state["districtData"][dist]["confirmed"])
        new_case = str(state["districtData"][dist]["delta"]["confirmed"])
        death = str(state["districtData"][dist]["delta"]["deceased"])
        recovered = str(state["districtData"][dist]["recovered"])
        print(recovered)
        context.bot.send_message(chat_id=update.message.chat_id,text="You are currently located in or the Map location shared is in *"+dist+"*\
        \nThe number of *confirmed* cases in this district are: *"+confirmed_d+"*\
        \nThe number of *new* cases are: *"+new_case+"*\
        \nThe number of *deaths* are: *"+death+"*\
        \nThe number of *recovered* people are: *"+recovered+"*\
        \nthis data was last updated at *"+last_updated_time+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You requested for *"+dist+"* district for which there are no stats at the moment")

    logger.info("location for district handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def us_statewise(update, context):
    var = ' '.join(context.args)
    print(var)
    if var == "":
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a Letter to list the US state names , Ex: '/ListUSAStates N",parse_mode=telegram.ParseMode.MARKDOWN)
    elif (var.isdigit()):
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a Letter to list the US state names , Ex: '/ListUSAStates N",parse_mode=telegram.ParseMode.MARKDOWN)
    elif(regex.search(var)) == None:
        letter = var.capitalize()
        print(letter)
        state_us = []
        code_us = []
        stateCount = str(len(jstates))
        for each in jstates:   
            US_state_name = str(each["name"]) 
            if US_state_name.startswith(letter):
                state_us.append(each["name"])
                code_us.append(each["state"])

        StateName_StateCode = ' \n'.join(["For "+ str(a) +" use code "+ b for a,b in zip(state_us,code_us)])
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="There are *"+stateCount+"* States in USA. Below are the names starting with letter *"+letter+"* and their codes\n\n\n*"+StateName_StateCode+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a Letter to list the US state names , Ex: '/ListUSAStates N",parse_mode=telegram.ParseMode.MARKDOWN)
    logger.info("US State code handler used ", update.message.chat.id, update.message.from_user.first_name)   
    captureID(update)

def us_statewise_stats(var):
    
    for each in states_us:
        if str(each["state"]) == var:
           confirmed = str(each["positive"]) 
           deaths = str(each["death"]) 
           recovered = str(each["recovered"])
           lastupdatedtime = str(each["lastUpdateEt"])
    return confirmed,deaths,recovered,lastupdatedtime

def getUS_stateName(var):
    for each in jstates:
        if str(each["state"]) == var:   
            state_name1 = str(each["name"])
    return state_name1

def usa_state(update, context):
    us_state_code = ' '.join(context.args).upper()
    print(us_state_code)
    if (us_state_code.isdigit()):
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a statecode, Ex: '/USAState AK'",parse_mode=telegram.ParseMode.MARKDOWN)
    elif us_state_code == "":
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a statecode, Ex: '/USAState AK'",parse_mode=telegram.ParseMode.MARKDOWN)
    elif(regex.search(us_state_code)) == None:
        content_k = us_statewise_stats(us_state_code)
        sN = getUS_stateName(us_state_code)
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.effective_chat.id, text="The number of *confirmed* cases in *"+sN+"* are: *"+content_k[0]+"*\
        \nThe number of *deaths* in this state are: *"+content_k[1]+"*\
        \nThe number of *recovered* people in this state are: *"+content_k[2]+"*\
        \nThis data was last updated at : *2020/"+content_k[3]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text="Add a statecode correctly , Ex: '/USAState AK",parse_mode=telegram.ParseMode.MARKDOWN)   
    logger.info("State handler used ", update.message.chat.id, update.message.from_user.first_name)
    print("This User checked "+sN+":"+update.message.from_user.first_name)
    captureID(update)

def continent_count(var):
    for each in continent_v:
        if str(each["continent"]) == var:
           confirmed = str(each["cases"]) 
           deaths = str(each["deaths"]) 
           recovered = str(each["recovered"])
           deltaconfirmed = str(each["todayCases"])
           deltadeaths = str(each["todayDeaths"])
           lastUpdatedTime = str(datetime.fromtimestamp((each["updated"])/1000).replace(microsecond=0))
    return confirmed,deaths,recovered,deltaconfirmed,deltadeaths,lastUpdatedTime

def asia(update, context):
    continentCount = continent_count("Asia")
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="The total number of *infected* people in *Asia* are: *"+continentCount[0]+"*\
    \nThe total number of *deaths* are: *"+continentCount[1]+"*\
    \nThe total number of *recovered* people are: *"+continentCount[2]+"*\
    \nThe number of *newcases* as of today are: *"+continentCount[3]+"*\
    \nThe number of *deaths* as of today are: *"+continentCount[4]+"*\
    \nThis data was last updated at of : *"+continentCount[5]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    print("This User checked Asia: "+update.message.from_user.first_name)
    logger.info("Asia handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def africa(update, context):
    continentCount = continent_count("Africa")
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="The total number of *infected* people in *Africa* are: *"+continentCount[0]+"*\
    \nThe total number of *deaths* are: *"+continentCount[1]+"*\
    \nThe total number of *recovered* people are: *"+continentCount[2]+"*\
    \nThe number of *newcases* as of today are: *"+continentCount[3]+"*\
    \nThe number of *deaths* as of today are: *"+continentCount[4]+"*\
    \nThis data was last updated at of : *"+continentCount[5]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    print("This User checked Asia: "+update.message.from_user.first_name)
    logger.info("Africa handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def northamerica(update, context):
    continentCount = continent_count("North America")
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="The total number of *infected* people in *North America* are: *"+continentCount[0]+"*\
    \nThe total number of *deaths* are: *"+continentCount[1]+"*\
    \nThe total number of *recovered* people are: *"+continentCount[2]+"*\
    \nThe number of *newcases* as of today are: *"+continentCount[3]+"*\
    \nThe number of *deaths* as of today are: *"+continentCount[4]+"*\
    \nThis data was last updated at of : *"+continentCount[5]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    print("This User checked Asia: "+update.message.from_user.first_name)
    logger.info("North America handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def europe(update, context):
    continentCount = continent_count("Europe")
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="The total number of *infected* people in *Europe* are: *"+continentCount[0]+"*\
    \nThe total number of *deaths* are: *"+continentCount[1]+"*\
    \nThe total number of *recovered* people are: *"+continentCount[2]+"*\
    \nThe number of *newcases* as of today are: *"+continentCount[3]+"*\
    \nThe number of *deaths* as of today are: *"+continentCount[4]+"*\
    \nThis data was last updated at of : *"+continentCount[5]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    print("This User checked Asia: "+update.message.from_user.first_name)
    logger.info("Europe handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def southamerica(update, context):
    continentCount = continent_count("South America")
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="The total number of *infected* people in *South America* are: *"+continentCount[0]+"*\
    \nThe total number of *deaths* are: *"+continentCount[1]+"*\
    \nThe total number of *recovered* people are: *"+continentCount[2]+"*\
    \nThe number of *newcases* as of today are: *"+continentCount[3]+"*\
    \nThe number of *deaths* as of today are: *"+continentCount[4]+"*\
    \nThis data was last updated at of : *"+continentCount[5]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    print("This User checked Asia: "+update.message.from_user.first_name)
    logger.info("South America handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def australia(update, context):
    continentCount = continent_count("Oceania")
    chat_id = update.message.chat_id
    context.bot.sendChatAction(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="The total number of *infected* people in *Australia* are: *"+continentCount[0]+"*\
    \nThe total number of *deaths* are: *"+continentCount[1]+"*\
    \nThe total number of *recovered* people are: *"+continentCount[2]+"*\
    \nThe number of *newcases* as of today are: *"+continentCount[3]+"*\
    \nThe number of *deaths* as of today are: *"+continentCount[4]+"*\
    \nThis data was last updated at of : *"+continentCount[5]+"*",parse_mode=telegram.ParseMode.MARKDOWN)
    print("This User checked Asia: "+update.message.from_user.first_name)
    logger.info("Australia handler used ", update.message.chat.id, update.message.from_user.first_name)
    captureID(update)

def main():
    BotToken = ""
    updater = Updater(BotToken,use_context=True)
    
    print (today)
    dp = updater.dispatcher
    logging.basicConfig(
        filename="bot.log",
        filemode="w",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    dp.add_handler(CommandHandler('start',start))
    dp.add_handler(CommandHandler('help',help))
    dp.add_handler(CommandHandler('india',india))
    dp.add_handler(CommandHandler('state',indianstate))
    dp.add_handler(CommandHandler('world',world))
    dp.add_handler(CommandHandler('statecode',indian_state_code))
    dp.add_handler(CommandHandler('countrycode',country_code))
    dp.add_handler(CommandHandler('country',countryWiseData))
    dp.add_handler(CommandHandler('official_TC',officialTelegramChannels))
    dp.add_handler(CommandHandler('topD',topD))
    dp.add_handler(CommandHandler('topC',topC))
    dp.add_handler(CommandHandler('districtwise',districtwise))
    dp.add_handler(CommandHandler('ListUSAStates',us_statewise))
    dp.add_handler(CommandHandler('USAState',usa_state))
    dp.add_handler(CommandHandler('asia',asia))
    dp.add_handler(CommandHandler('africa',africa))
    dp.add_handler(CommandHandler('europe',europe))
    dp.add_handler(CommandHandler('northamerica',northamerica))
    dp.add_handler(CommandHandler('southamerica',southamerica))
    dp.add_handler(CommandHandler('australia',australia))
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_handler(MessageHandler(Filters.location,getLocation))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()