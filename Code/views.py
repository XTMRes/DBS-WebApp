from django.http import HttpResponse
from django.http import JsonResponse

import os
import psycopg2
import json

def index(request):
    return HttpResponse("Please navigate to fiit-dbs-xlehocky-app.azurewebsites.net/v1/health")

def health(request):
    conn = psycopg2.connect(host="147.175.150.216",database="dota2",user="xlehocky",password=os.getenv("AISPASS"))
    curr = conn.cursor()
    curr.execute('SELECT VERSION();')
    ver = curr.fetchone()
    curr.execute("SELECT pg_database_size('dota2')/1024/1024 as dota2_db_size;")
    size = curr.fetchone()
    data = dict({"version":"".join(ver), "dota2_db_size":"".join(str(int(size[0])))})
    data = dict({"pgsql":data})
    curr.close()
    conn.close()
    return JsonResponse((data),safe = False)

def patches(request):
    conn = psycopg2.connect(host="147.175.150.216",database="dota2",user="xlehocky",password=os.getenv("AISPASS"))
    curr = conn.cursor()
    curr.execute("select patches.name as patch_version, cast(extract(epoch from(patches.release_date at time zone 'UTC'))as int) as patch_start_date, cast(extract(epoch from(enddates.release_date at time zone 'UTC'))as int) as patch_end_date, matches.id as match_id, cast(trunc(cast(matches.duration*100.0/60/100.0+0.005 as numeric),2)as float) as match_duration from patches left join patches as enddates on patches.id = enddates.id-1 left join matches on (extract(epoch from(patches.release_date at time zone 'UTC')) < matches.start_time and matches.start_time < extract(epoch from(enddates.release_date at time zone 'UTC'))) order by patches.id asc")
    data = curr.fetchall()
    patches = list()
    for row in data:
        insert = True
        for i in range(len(patches)):
            if patches[i]["patch_version"] == row[0]:
                insert = False             
        if insert:
            matchlist = list()
            for row_2 in data:
                if row[0] == row_2[0] and row_2[3] is not None:
                    matchlist.append({"match_id" : row_2[3], "duration" : row_2[4]})
            if {"match_id": None, "duration": None} not in matchlist:
                patches.append({"patch_version" : row[0], "patch_start_date" : row[1], "patch_end_date" : row[2], "matches" : matchlist})
    result = {"patches" : patches}
    curr.close()
    conn.close()
    return JsonResponse(result,safe = False)

def game_exp(request,playerid):
    conn = psycopg2.connect(host="147.175.150.216",database="dota2",user="xlehocky",password=os.getenv("AISPASS"))
    curr = conn.cursor()
    curr.execute("select players.id,COALESCE(players.nick,'unknown'),mpd.match_id,heroes.localized_name,cast(trunc(cast(matches.duration*100.0/60/100.0+0.005 as numeric),2)as float) , COALESCE(mpd.xp_hero,0) + COALESCE(mpd.xp_creep,0) + COALESCE(mpd.xp_other,0) + COALESCE(mpd.xp_roshan,0) as experiences_gained, level,matches.radiant_win and (mpd.player_slot < 5 and mpd.player_slot >= 0) or (not matches.radiant_win and mpd.player_slot < 133 and mpd.player_slot >= 128) from players join matches_players_details as mpd on mpd.player_id = players.id join heroes on heroes.id = mpd.hero_id join matches on matches.id = mpd.match_id where players.id = "+str(playerid)+" order by mpd.match_id asc;" )
    data = curr.fetchall()
    matchlist = list()
    for row in data:
        matchlist.append({"match_id" : row[2], "hero_localized_name" : row[3], "match_duration_minutes" : row[4], "experiences_gained" : row[5], "level_gained" : row[6], "winner" : row[7]})
    player = {"id" : row[0], "player_nick" : row[1], "matches" : matchlist}
    curr.close()
    conn.close()
    return JsonResponse(player,safe = False)

def game_objectives(request,playerid):
    conn = psycopg2.connect(host="147.175.150.216",database="dota2",user="xlehocky",password=os.getenv("AISPASS"))
    curr = conn.cursor()
    curr.execute("select players.id,COALESCE(players.nick,'unknown') as player_nick,heroes.localized_name as hero_localized_name,matches.id as match_id,COALESCE(game_objectives.subtype,'NO_ACTION') as hero_action,COUNT(*) from matches_players_details join heroes on heroes.id = matches_players_details.hero_id join matches on matches.id = matches_players_details.match_id  join players on players.id = matches_players_details.player_id left join game_objectives on match_player_detail_id_1 = matches_players_details.id where players.id = "+str(playerid)+" group by players.id,players.nick,matches.id,heroes.localized_name,matches.id,game_objectives.subtype order by matches.id asc")
    data = curr.fetchall()
    matchlist = list()
    for row in data:
        insert = True
        for i in range(len(matchlist)):
            if matchlist[i]["match_id"] == row[3]:
                insert = False             
        if insert:
            subtypes = list()
            for row_2 in data:
                if row[3] == row_2[3]:
                    if {"hero_action" : row_2[4], "count" : row_2[5]} not in subtypes:
                        subtypes.append({"hero_action" : row_2[4], "count" : row_2[5]})
            matchlist.append({"match_id" : row[3], "hero_localized_name" : row[2],"actions" : subtypes})
    player = {"id" : row[0], "player_nick" : row[1], "matches" : matchlist}
    curr.close()
    conn.close()
    return JsonResponse(player,safe = False)

def abilities(request,playerid):
    conn = psycopg2.connect(host="147.175.150.216",database="dota2",user="xlehocky",password=os.getenv("AISPASS"))
    curr = conn.cursor()
    curr.execute("select players.id,COALESCE(players.nick,'unknown') as player_nick,heroes.localized_name as hero_localized_name,matches.id as match_id,abilities.name as ability_name,COUNT(*), max(au.level) as upgrade_level from matches_players_details join heroes on heroes.id = matches_players_details.hero_id join matches on matches.id = matches_players_details.match_id join players on players.id = matches_players_details.player_id left join ability_upgrades as au on au.match_player_detail_id = matches_players_details.id join abilities on abilities.id = au.ability_id where players.id = "+str(playerid)+" group by players.id,players.nick,matches.id,heroes.localized_name,matches.id,abilities.name order by matches.id asc;")
    data = curr.fetchall()
    matchlist = list()
    for row in data:
        insert = True
        for i in range(len(matchlist)):
            if matchlist[i]["match_id"] == row[3]:
                insert = False             
        if insert:
            abilities = list()
            for row_2 in data:
                if row[3] == row_2[3]:
                    if {"hero_action" : row_2[4], "count" : row_2[5]} not in abilities:
                        abilities.append({"ability_name" : row_2[4], "count" : row_2[5],"upgrade_level" : row_2[6]})
            matchlist.append({"match_id" : row[3], "hero_localized_name" : row[2],"abilities" : abilities})
    player = {"id" : row[0], "player_nick" : row[1], "matches" : matchlist}
    curr.close()
    conn.close()
    return JsonResponse(player,safe = False)

def purchases(request,matchid):
    conn = psycopg2.connect(host="147.175.150.216",database="dota2",user="xlehocky",password=os.getenv("AISPASS"))
    curr = conn.cursor()
    curr.execute("select * from ( select heroes.localized_name,heroes.id as heroid,items.name, items.id,count(logs.item_id), ROW_NUMBER() OVER (partition by heroes.localized_name order by count(logs.item_id) desc,items.name) as num from matches join matches_players_details as mpd on mpd.match_id = matches.id left join heroes on mpd.hero_id = heroes.id left join purchase_logs as logs on match_player_detail_id = mpd.id join items on logs.item_id = items.id where ((mpd.player_slot >= 128 and not matches.radiant_win) or (mpd.player_slot <= 4 and matches.radiant_win)) and matches.id = "+str(matchid)+" Group by heroes.localized_name,heroes.id,mpd.hero_id,items.name,items.id )x where x.num <= 5 order by x.heroid,x.count desc, x.name")
    data = curr.fetchall()
    heroes = list()
    for row in data:
        insert = True
        for i in range(len(heroes)):
            if heroes[i]["name"] == row[0]:
                insert = False             
        if insert:
            purchases = list()
            for row_2 in data:
                if row[1] == row_2[1]:
                    if {"name" : row_2[2],"id" : row_2[3], "count" : row_2[4]} not in purchases:
                        purchases.append({"name" : row_2[2], "id" : row_2[3], "count" : row_2[4]})
            heroes.append({"id" : row[1], "name" : row[0] ,"top_purchases" : purchases})
    response = {"heroes" : heroes,"id": matchid}
    curr.close()
    conn.close()
    return JsonResponse(response,safe = False)

def ability_usage(request,abilityid):
    response = {"Ability" : abilityid}
    return JsonResponse(response,safe = False)

def tower_kills(request):
    response = {"Placeholder" : None}
    return JsonResponse(response,safe = False)