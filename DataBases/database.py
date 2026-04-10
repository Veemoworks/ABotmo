import datetime, mssql_python as sql, discord, random, json, string, os, dotenv
dotenv.load_dotenv(".env")

uuidFormat = "____-___-______-___"
uuidChars = [char for char in string.ascii_lowercase[:6] + string.digits]
columns = {
    "modlogs": """[user]    BIGINT,
        mod       BIGINT,
        reason    varchar(max),
        message   varchar(max),
        type      varchar(max),
        timestamp int,
        i         int,
        id        varchar(max)""",
    "xp": """[user] BIGINT,
        xp BIGINT,
        level int,
        last_msg int""",
    "xp_settings": """guild_id BIGINT,
        messagetoggle bit,
        channel BIGINT,
        cd TINYINT,
        range varchar(max),
        xpenabled bit""",
    "xp_roles": """guild_id BIGINT,
        data varchar(max)""",
    "server_settings": """guild_id BIGINT,
        roles varchar(max),
        prefix varchar(max),
        casenum int""",
    "user_settings": """user BIGINTY,
        xpmessage tinyint""",
    "server_channels": """guild_id BIGINT,
            modlog BIGINT,
            member BIGINT,
            message BIGINT,
            channel BIGINT,
            role BIGINT,
            voice BIGINT""",
    "webhooks": """id BIGINT,
            token varchar(max),
            channel BIGINT""",
}

def connectToDB(database: str):
    if not database:
        return None, None
    db = sql.connect(f"Server={os.getenv("MSSQLHost")};Database={database};UID={os.getenv("MSSQLUID")};PWD={os.getenv("MSSQLPWD")};TrustServerCertificate=yes;", timeout=300)
    return db, db.cursor()

def getUUID():
    con, cur = connectToDB("modlogs")
    uuid = ""
    while True:
        uuid = ""
        for ch in uuidFormat: # UUID format
            if ch == "_":
                uuid += random.choice(uuidChars)
            else:
                uuid += ch
        temp = cur.execute(f"SELECT id FROM main.modlogIds WHERE id = '{uuid}'").fetchone()
        if not temp:
            break
    cur.execute(f"INSERT INTO main.modlogIds (id) VALUES ('{uuid}')").commit()
    con.close()
    return uuid

def checkTableExists(con: sql.db_connection.Connection, cur: sql.cursor.Cursor, name: str, db_name: str):
    cur.execute(f"""
    if not exists(select * from sys.tables where name='{name}')
        create table main.[{name}]
        (
            {columns[db_name]}
        )"""
    )
    con.commit()

def modlog(save, interaction: discord.Interaction, data = None, user: discord.User | discord.Member = None, rem = False):
    msg = None
    con, cur = connectToDB("modlogs")
    gid = str(interaction.guild.id)
    checkTableExists(con, cur, gid, "modlogs")

    if save and not rem:
        i = len(cur.execute(f"""
            SELECT * FROM main.[{gid}] WHERE [user] = '{data[0]}'""").fetchall()) + 1
        data.append(i)
        uuid = getUUID()
        data.append(uuid)
        cur.execute(f"""
            INSERT INTO main.[{gid}] ([user], mod, reason, message, type, timestamp, i, id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, data)
        con.commit()
        msg = (f"Successfully gave <@{data[0]}> a {data[4].lower()}, they now have {i} modlogs!\n-# Modlog ID: {uuid}", uuid)
    elif not save and not rem:
        if data[1]:
            msg = discord.Embed(color=discord.Color.dark_green())
            msg.set_author(name=f"LOG '{data[1]}' DETAILS")
            cur.execute(f"SELECT * FROM main.[{gid}] WHERE id = '{data[1]}'")
            row = cur.fetchone()
            if row:
                user = interaction.guild.get_member(row[0])
                msg.author.icon_url = user.avatar.url if user and user.avatar else None
                msg.description = f"<t:{row[5]}:R>, <@{row[1]}> issued a **{row[4]}** on <@{row[0]}>"
                msg.add_field(name="Index:", value=row[6])
                msg.add_field(name="Reason:", value=row[2])
                msg.add_field(name="Message:", value=row[3])
                msg.set_footer(text=f"User ID: {row[0]} | Mod ID: {row[1]}")
                msg.timestamp = datetime.datetime.fromtimestamp(row[5])
            else:
                msg.description = "Moderation Log not found! Ensure the ID is correct."
        elif data[2] and user:
            cur.execute(f"""
                            SELECT type, timestamp, [user], id
                            FROM main.[{gid}]
                            WHERE mod = '{user.id}'
                        """)
            rows = cur.fetchall()
            msg = discord.Embed(color=discord.Color.dark_green())
            msg.set_author(name=user.name, icon_url=user.avatar.url if user.avatar else None)
            if not rows == []:
                tpages = 1
                target = 26
                for i in range(len(rows)):
                    if i == target:
                        tpages += 1
                        target += 25
                if data[0] > tpages:
                    data[0] = tpages
                msg.description = f"Page {data[0]} / {tpages}\n-# Each page is 25 modlogs - TOTAL LOGS: {len(rows)}"
                rows = rows[25 * (data[0] - 1):25 * data[0]]
                i = 0
                for row in rows:
                    i += 1
                    msg.add_field(name=f"{i+(target-26)}. <t:{row[1]}>",
                                  value=f"**{row[0]}** on <@{row[2]}> ~ {row[3]}",
                                  inline=False)
                msg.set_footer(text=user.id)
            else:
                msg.description = f"No moderation logs from {user.mention} found!"
        else:
            cur.execute(f"""
                SELECT type, timestamp, i, id
                FROM main.[{gid}]
                WHERE [user] = '{user.id}'
                ORDER BY i;
            """)
            rows = cur.fetchall()
            msg = discord.Embed(color=discord.Color.dark_green())
            msg.set_author(name=user.name, icon_url=user.avatar.url if user.avatar else None)
            if not rows == []:
                tpages = 1
                target = 26
                for i in range(len(rows)):
                    if i == target:
                        tpages += 1
                        target += 25
                if data[0] > tpages:
                    data[0] = tpages
                msg.description = f"Page {data[0]} / {tpages}\n-# Each page is 25 modlogs - TOTAL LOGS: {len(rows)}"
                rows = rows[25 * (data[0]-1):25 * data[0]]
                for row in rows:
                    msg.add_field(name=f"{row[2]}. <t:{row[1]}>", value=f"{row[0]} | {row[3]}", inline=False)
                    msg.set_footer(text=user.id)
            else:
                msg.description = f"No modlogs found for {user.mention}!"
    elif save and rem:
        msg = (
            f"Could not find Log '`{data}`', an error occured, or no user was specified.\nEnsure the Log ID exists, is from this server, or the user is correct.\n-# *User only required if you're deleting all logs.*",
            False, user)
        print(data, user)
        if data.strip() == "*" and user:
            cur.execute(f"""DELETE FROM main.[{gid}] WHERE user = {user.id}""")
            msg = (f"Successfully deleted all of {user.mention}'s logs!", True, user)
        elif not data.strip().find("-") == -1:
            cur.execute(f"""
                    SELECT [user] FROM main.[{gid}] WHERE id = '{data}'"""
                    )
            t = cur.fetchone()
            if t:
                cur.execute(f"""
                    DELETE FROM main.[{gid}] WHERE id = '{data}'""")
                msg = (f"Successfully deleted Log '{data}' from the Discord Server's database!", True, t[0], len(cur.execute(f"""SELECT * FROM main.[{gid}] WHERE user = '{t[0]}'""").fetchall()))
        con.commit()
    elif not save and rem:
        cur.execute(f"""
                        SELECT i
                        FROM main.[{gid}]
                        WHERE [user] = '{user.id}'
                    """)
        msg = len(cur.fetchall())
    con.close()
    return msg

# <editor-fold desc="xp.db">
def nextLevel(level: int):
    return 5 * (level**2) + (level * 50) + 75

def xp(save, guild, data=None, user=None, lvlup=True):
    returnval = None
    con, cur = connectToDB("xp")
    gid = str(guild.id)
    checkTableExists(con, cur, gid, "xp")

    if save:
        if lvlup:
            cur.execute(f"""
                        SELECT xp, level, last_msg FROM main.[{gid}]
                        WHERE [user] = '{user.id}'   
                    """)
            row = cur.fetchone()
            if row == None:
                t: dict = xp_settings(False, guild, None)
                cur.execute(f"""
                            INSERT INTO main.[{gid}]
                            VALUES ({user.id}, {random.randint(t["range"][0], t["range"][1])}, 0, {data})
                            """)
                con.commit()
                level = 0
            else:
                g: dict = xp_settings(False, guild, None)
                xph, level, last_msg = row
                if last_msg is None or data - last_msg >= g["cd"]:
                    new_xp = xph + random.randint(g["range"][0], g["range"][1])
                    next_level = nextLevel(level)

                    if new_xp >= next_level:
                        level += 1
                        returnval = True

                    cur.execute(f"""
                                UPDATE main.[{gid}]
                                SET xp = '{new_xp}', level = '{level}', last_msg = '{data}'
                                WHERE [user] = '{user.id}'
                            """)
                    con.commit()
            con.close()
            return returnval, level
        else:
            newxp, newlevel = data
            cur.execute(f"""
                        UPDATE main.[{gid}]
                        SET {f"xp = '{newxp}'" if newxp else ""}{", " if newlevel and newxp else ""}{f"level = '{newlevel}'" if newlevel else ""}
                        WHERE [user] = '{user.id}' 
                    """)
            con.commit()
            con.close()
            return [newxp, newlevel]
    else:
        cur.execute(f"""
            SELECT xp, level FROM main.[{gid}]
            WHERE [user] = '{user.id}'
        """)

        row = cur.fetchone()

        if row == None:
            return False, None

        dxp, level = row
        next_level = nextLevel(level)
        con.close()
        return True, [dxp, level, next_level]

def xp_settings(save, guild: discord.Guild, data):
    con, cur = connectToDB("xp")
    gid = guild.id
    checkTableExists(con, cur, "xp_settings", "xp_settings")

    cur.execute(f"SELECT * FROM main.[xp_settings] WHERE guild_id = {gid}")
    row = cur.fetchone()

    if not row:
        cur.execute(f"""
            INSERT INTO main.[xp_settings] (guild_id)
            VALUES ({gid});
        """)
        con.commit()

    # togglable messages - messagetoggle
    # channel conifg (where lvl up is sent) - channel
    # cd for xp - cd
    # range of xp - range
    # xpenabled thing

    if save:
        changes = {}
        for datatype, vals in data.items():
            changed, val = vals
            if not changed:
                continue
            cur.execute(f"""
                    UPDATE main.[xp_settings]
                    SET {datatype} = {val}
                    WHERE guild_id = {gid}
            """)
            con.commit()
            changes[datatype] = val
        con.close()
        kirk = {
            "messagetoggle": "Level Up message",
            "channel": "Level Up channel",
            "cd": "XP cooldown",
            "range": "XP range",
            "xpenabled": "XP Toggle",
            "channelnums": {
                1: "current channel",
                2: guild.get_channel(data["channel"][1])
            }
        }

        if not changes:
            return "No XP setting changes were made!"
        text = []
        for key, val in changes.items():
            _type = type(val)
            if key == "channel":
                if val > 1:
                    val = kirk["channelnums"][2].mention
                else:
                    val = kirk["channelnums"][1]
            elif _type == int:
                if val:
                    val = "On"
                else:
                    val = "Off"
            elif _type == str:
                temp = json.loads(val.strip("'"))
                val = f"{temp[0]} to {temp[1]}"
            text.append(f"{kirk[key]} was set to {val}")

        return "\n".join(text)
    else:
        cur.execute(f"""
            SELECT *
            FROM main.[xp_settings]
            WHERE guild_id = {gid};
        """)
        data = cur.fetchone()
        con.close()

        if data == "messagetoggle":
            return data[1]
        elif data == "channel":
            return data[2]
        elif data == "cd":
            return data[3]
        elif data == "range":
            return json.loads(data[4])
        elif data == "xpenabled":
            return data[5]
        else:
            return {
                "messagetoggle": data[1],
                "channel": data[2],
                "cd": data[3],
                "range": json.loads(data[4]),
                "xpenabled": data[5]
            }

def xp_roles(save, guild: discord.Guild, level=None, role=None):
    con, cur = connectToDB("xp")
    gid = guild.id
    checkTableExists(con, cur, "xp_roles", "xp_roles")

    cur.execute(f"SELECT * FROM main.[xp_roles] WHERE guild_id = {gid}")
    row = cur.fetchone()
    role = str(role)
    if not row:
        cur.execute(f"""
            INSERT INTO main.[xp_roles] (guild_id)
            VALUES ({gid});
        """)
        con.commit()
    if save:
        level = str(level)
        val = False
        cur.execute(f"SELECT data FROM main.[xp_roles] WHERE guild_id = {gid}")
        data: dict = json.loads(cur.fetchone()[0].replace("'", '"'))
        if role in data.values():
            key = None
            for k, v in data.items():
                if role == v:
                    key = k
            data.pop(key)
            data[level] = role
            val = False
        else:
            data[level] = role
            val = True
        cur.execute(f"UPDATE main.[xp_roles] SET data = \"{str(data)}\" WHERE guild_id = {gid}")
        con.commit()
        con.close()
        return val
    else:
        cur.execute(f"SELECT data FROM main.[xp_roles] WHERE guild_id = {gid}")
        data = json.loads(cur.fetchone()[0].replace("'", '"'))
        if not level is None:
            data = data.get(str(level))
        con.close()
        return data
# </editor-fold>

# <editor-fold desc="settings.db">
def server_settings(save, guild, stype=None, value=None):
    con, cur = connectToDB("settings")
    gid = str(guild.id)
    checkTableExists(con, cur, "server_settings", "server_settings")

    cur.execute(f"SELECT * FROM main.[server_settings] WHERE guild_id = {gid}")
    row = cur.fetchone()

    if not row:
        cur.execute(f"""
            INSERT INTO main.[server_settings] (guild_id, roles, prefix, casenum)
            VALUES ({gid}, '[]', ';;', 0);
        """)
        con.commit()

    if save:

        if stype == "roles":
            cur.execute("SELECT roles FROM main.[server_settings] WHERE guild_id = ?", (gid,))
            roles = json.loads(cur.fetchone()[0])

            role = str(value)

            if role in roles:
                roles.remove(role)
                msg = f"Removed <@&{role}> from the server config."
            else:
                roles.append(role)
                msg = f"Added <@&{role}> to the server config."

            cur.execute("""
                UPDATE main.[server_settings]
                SET roles = ?
                WHERE guild_id = ?;
            """, (json.dumps(roles), gid))

            con.commit()
            con.close()
            return msg
        elif stype == "prefix":
            cur.execute("""
                UPDATE main.[server_settings]
                SET prefix = ?
                WHERE guild_id = ?;
            """, (value, gid))

            con.commit()
            con.close()
            return f"Your server configuration for bot prefix has been updated to \"{value}\"."
        elif stype == "casenum":
            cur.execute(f"""
                SELECT casenum FROM main.[server_settings] WHERE guild_id = {gid}""")
            num = cur.fetchone()[0]
            num += 1
            cur.execute(f"""
                UPDATE main.[server_settings]
                SET casenum = ?
                WHERE guild_id = ?;
            """, (num, gid))
            con.commit()
            con.close()
            return num
        elif stype == "banned":
            cur.execute(f"SELECT banned FROM main.[server_settings] WHERE guild_id = {gid}")
            banned: list = json.loads(cur.fetchone()[0])

            if value in banned:
                banned.remove(value)
                msg = f"Removed {value} from the banned word list."
            else:
                banned.append(value)
                msg = f"Added {value} to the banned word list."

            cur.execute(f"UPDATE main.[server_settings] SET banned = '{json.dumps(banned)}' WHERE guild_id = {gid}")

            con.commit()
            con.close()
            return msg
        else:
            return "fella..."
    else:
        cur.execute("""
            SELECT roles, prefix, casenum, banned
            FROM main.[server_settings]
            WHERE guild_id = ?;
        """, (gid,))
        data = cur.fetchone()
        con.close()

        if stype == "roles":
            return json.loads(data[0])
        elif stype == "prefix":
            return data[1]
        elif stype == "casenum":
            return data[2]
        elif stype == "banned":
            return json.loads(data[3])
        else:
            return {
                "roles": json.loads(data[0]),
                "prefix": data[1],
                "casenum": data[2],
                "banned": json.loads(data[3]),
            }

def user_settings(save, userid: int, setting, data=None):
    returnval = False
    con, cur = connectToDB("settings")
    checkTableExists(con, cur, "user_settings", "user_settings") # temp - 0 = off, 1 = on (server), 2 = on (dms)

    cur.execute(f"SELECT * FROM main.[user_settings] WHERE user = {userid}")
    row = cur.fetchone()

    if not row:
        cur.execute(f"""
            INSERT INTO main.[user_settings] (user, xpmessage)
            VALUES ({userid}, 1);
        """)
        con.commit()

    if save:
        if setting == "xpmessage":
            cur.execute(f"""
                        SELECT xpmessage
                        FROM main.[user_settings]
                        WHERE user = {userid}
            """)
            if not cur.fetchone()[0] == data:
                cur.execute(f"""
                            UPDATE user_settings
                            SET xpmessage = {data}
                            WHERE user = {userid}
                        """)
                con.commit()
                returnval = True
    else:
        if setting == "xpmessage":
            cur.execute(f"""
                        SELECT xpmessage
                        FROM main.[user_settings]
                        WHERE user = {userid}
            """)
            returnval = cur.fetchone()[0]
    con.close()
    return returnval

def server_channels(save, guild, channel, data=None):
    con, cur = connectToDB("settings")
    gid = guild.id
    checkTableExists(con, cur, "server_channels", "server_channels")

    cur.execute(f"SELECT * FROM main.[server_channels] WHERE guild_id = {gid}")
    row = cur.fetchone()
    if not row:
        cur.execute(f"""
            INSERT INTO main.[server_channels] (guild_id, [modlog], member, message, channel, role, voice, guild)
            VALUES ({gid}, 0, 0, 0, 0, 0, 0);
        """)
        con.commit()
    if save:
        if channel == "all event":
            cur.execute(f"""
                UPDATE server_channels
                SET modlog = {data},
                    member = {data},
                    message = {data},
                    channel = {data},
                    role = {data},
                    voice = {data},
                    guild = {data}
                WHERE guild_id = {gid};
            """)
            con.commit()
            con.close()
            return f"All events have been set to channel \"<#{data}>\""

        cur.execute(f"SELECT {channel} FROM main.[server_channels] WHERE guild_id = {gid}")
        current = cur.fetchone()[0]

        if current == data:
            cur.execute(f"""
                        UPDATE main.[server_channels]
                        SET {channel} = NULL
                        WHERE guild_id = {gid};
                """)
            msg = f"Deleted \"<#{data}>\" from the {channel} event server config."
        else:
            cur.execute(f"""
                        UPDATE main.[server_channels]
                        SET {channel} = {data}
                        WHERE guild_id = {gid};
                """)
            msg = f"Your new {channel} event channel is: \"<#{data}>\"."
        con.commit()
        con.close()
        return msg
    else:
        cur.execute(f"""
                    SELECT *
                    FROM main.[server_channels]
                    WHERE guild_id = {gid};
                """)
        data = cur.fetchone()
        con.close()

        if channel == "modlog":
            return data[1]
        elif channel == "member":
            return data[2]
        elif channel == "message":
            return data[3]
        elif channel == "channel":
            return data[4]
        elif channel == "role":
            return data[5]
        elif channel == "voice":
            return data[6]
        elif channel == "guild":
            return data[7]
        else:
            return {
                "modlog": data[1],
                "member": data[2],
                "message": data[3],
                "channel": data[4],
                "role": data[5],
                "voice": data[6],
                "guild": data[7],
            }
# </editor-fold>

def webhooks(save, guild, data):
    # data format = (id, token, name, channel)
    con, cur = connectToDB("webhooks")
    gid = guild.id
    checkTableExists(con, cur, gid, "webhooks")

    if save:
        cur.execute(f"""
                INSERT INTO main.[{gid}] (
                    id, token, channel
                ) VALUES ({data[0]}, '{data[1]}', {data[2]})
        """)
        con.commit()
        con.close()
        return True
    else:
        cur.execute(f"""
                SELECT * FROM main.[{gid}] WHERE channel = {data[0]} AND id = {data[1]}
        """)
        data = cur.fetchone()
        if data:
            con.close()
            return data
        con.close()
        return False