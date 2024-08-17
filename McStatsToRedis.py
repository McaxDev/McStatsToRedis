import sys
import redis
import json
import os

if len(sys.argv) != 2:
    print("用法：python 脚本名.py 配置文件路径.json")
    sys.exit(1)

with open(sys.argv[1], 'r', encoding='utf-8') as file:
    config = json.load(file)

def store(data, records_name, method, player_name):
    for record_name in records_name:
        full_record_name = 'minecraft:' + record_name
        if full_record_name in data:
            value = method(data[full_record_name])
            r.zadd(full_record_name, {player_name: value})

for server in config['mc_servers']:
    server_path = server['path']
    r = redis.Redis(db=server['db'], **config['redis'])
    r.flushdb()
    usercache_path = os.path.join(server_path, 'usercache.json')
    with open(usercache_path, 'r', encoding='utf-8') as file:
        usercache = json.load(file)
    uuid_map = {}
    for name_uuid in usercache:
        uuid_map[name_uuid['uuid']] = name_uuid['name']
    stats_folder = os.path.join(server_path, 'world/stats/')
    for filename in os.listdir(stats_folder):
        if filename.endswith('.json'):
            uuid, _ = os.path.splitext(filename)
            if uuid in uuid_map:
                player_name = uuid_map[uuid]
                stats_file = os.path.join(stats_folder, filename)
                with open(stats_file, 'r', encoding='utf-8') as file:
                    player_data = json.load(file)['stats']
                    store(
                        player_data, 
                        config['sumed_stats'], 
                        lambda x: sum(x.values()), 
                        player_name,
                    )
                    if 'minecraft:custom' in player_data:
                        store(
                            player_data['minecraft:custom'], 
                            config['custom_stats'], 
                            lambda x: x, 
                            player_name
                        )
