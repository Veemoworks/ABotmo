import sqlite3, discord, random, json

def modlog(save, interaction, data = None, user: discord.User | discord.Member = None, rem = False):
    msg = None
    con = sqlite3.connect("DataBases/modlogs.db")
    cur = con.cursor()
    guild_id = str(interaction.guild.id)
    cur.execute(f"""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = {guild_id};
                """)

    if not cur.fetchone():
        cur.execute(f"""
            CREATE TABLE '{guild_id}' (
                user TEXT,
                mod TEXT,
                reason TEXT,
                message TEXT,
                type TEXT,
                timestamp TEXT,
                i INTEGER
            );
        """)

    if save and not rem:
        i = len(cur.execute(f"""
            SELECT * FROM '{guild_id}' WHERE user = '{data[0]}'""").fetchall()) + 1
        data.append(i)
        cur.execute(f"""
            INSERT INTO "{guild_id}" (user, mod, reason, message, type, timestamp, i)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, data)
        con.commit()
        cur.execute(f"""
            SELECT * FROM '{guild_id}'
            WHERE user = '{str(data[0])}';
            """)
        msg = f"Successfully gave <@{data[0]}> a {data[4].lower()}, they now have {len(cur.fetchall())} modlogs!"
    elif not save and not rem:
        if data[1]:
            cur.execute(f"""
                            SELECT type, reason, message, timestamp, user, i
                            FROM '{guild_id}'
                            WHERE mod = '{user.id}'
                        """)
            rows = cur.fetchall()
            msg = discord.Embed(color=discord.Color.dark_green())
            msg.set_author(name=user.name, icon_url=user.display_avatar.url)
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
                    msg.add_field(name=f"{i}. <t:{row[3]}>",
                                  value=f"<@{row[4]}>: **{row[0]}** ~ \"{row[1]}\"{"" if row[2] is None else f' | MSG: "{row[2]}"'} - {row[5]}",
                                  inline=False)
                    msg.set_footer(text=user.id)
            else:
                msg.description = f"No moderation logs from {user.mention} found!"
        else:
            cur.execute(f"""
                SELECT type, reason, message, timestamp, mod, i
                FROM '{guild_id}'
                WHERE user = '{user.id}'
                ORDER BY i;
            """)
            rows = cur.fetchall()
            msg = discord.Embed(color=discord.Color.dark_green())
            msg.set_author(name=user.name, icon_url=user.display_avatar.url)
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
                    msg.add_field(name=f"{row[5]}. <t:{row[3]}>", value=f"{row[0]} | \"{row[1]}\"{""if row[2] is None else f' | MSG: "{row[2]}"'} ~ <@{row[4]}>", inline=False)
                    msg.set_footer(text=user.id)
            else:
                msg.description = f"No modlogs found for {user.mention}!"
    elif save and rem:
        cur.execute(f"""
            SELECT * FROM '{guild_id}' WHERE user = '{user.id}'"""
        )
        t = cur.fetchall()
        msg = (f"Could not find index {data} in {user.mention}'s modlogs.", False)
        if not t == []:
            if isinstance(data, int):
                for row in t:
                    if row == data:
                        cur.execute(f"""
                            DELETE FROM '{guild_id}' WHERE i = {data}""")
                        msg = (f"Successfully deleted index {data} from {user.mention}'s modlogs!", True)
                        break
            elif isinstance(data, str):
                cur.execute(f"""DELETE FROM '{guild_id}' WHERE user = {user.id}""")
                msg = (f"Successfully deleted all of {user.mention}'s logs!", True)

        con.commit()
    elif not save and rem:
        cur.execute(f"""
                        SELECT i
                        FROM '{guild_id}'
                        WHERE user = '{user.id}'
                    """)
        msg = len(cur.fetchall())
    con.close()
    return msg

# <editor-fold desc="xp.db">
def nextLevel(level: int):
    return 5 * (level**2) + (level * 50) + 75

def xp(save, guild, data=None, user=None, lvlup=True):
    returnval = None
    con = sqlite3.connect("DataBases/xp.db")
    cur = con.cursor()
    guild_id = str(guild.id)
    cur.execute(f"""
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = '{guild_id}';
        """)
    if not cur.fetchone():
        cur.execute(f"""
                CREATE TABLE '{guild_id}' (
                    user INTEGER,
                    xp INTEGER,
                    level INTEGER,
                    last_msg INTEGER
                );
            """)
        con.commit()

    if save:
        if lvlup:
            cur.execute(f"""
                        SELECT xp, level, last_msg FROM '{guild_id}'
                        WHERE user = '{user.id}'   
                    """)
            row = cur.fetchone()
            if row == None:
                t: dict = xp_settings(False, guild, None)
                cur.execute(f"""
                            INSERT INTO '{guild_id}'
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
                                UPDATE '{guild_id}'
                                SET xp = '{new_xp}', level = '{level}', last_msg = '{data}'
                                WHERE user = '{user.id}'
                            """)
                    con.commit()
            con.close()
            return returnval, level
        else:
            newxp, newlevel = data
            cur.execute(f"""
                        UPDATE '{guild_id}'
                        SET {f"xp = '{newxp}'" if newxp else ""}{", " if newlevel and newxp else ""}{f"level = '{newlevel}'" if newlevel else ""}
                        WHERE user = '{user.id}' 
                    """)
            con.commit()
            con.close()
            return [newxp, newlevel]
    else:
        cur.execute(f"""
            SELECT xp, level FROM '{guild_id}'
            WHERE user = '{user.id}'
        """)

        row = cur.fetchone()

        if row == None:
            return False, None

        dxp, level = row
        next_level = nextLevel(level)
        con.close()
        return True, [dxp, level, next_level]

def xp_settings(save, guild: discord.Guild, data):
    con = sqlite3.connect("DataBases/xp.db")
    cur = con.cursor()
    gid = guild.id
    cur.execute("""
        CREATE TABLE IF NOT EXISTS xp_settings (
            guild_id INTEGER PRIMARY KEY,
            messagetoggle INTEGER,
            channel INTEGER,
            cd INTEGER,
            range TEXT,
            xpenabled INTEGER
        );
    """)

    cur.execute("SELECT * FROM xp_settings WHERE guild_id = ?", (gid,))
    row = cur.fetchone()

    if not row:
        cur.execute(f"""
            INSERT INTO xp_settings (guild_id)
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
                    UPDATE xp_settings
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
            elif _type == bool:
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
            FROM xp_settings
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
    con = sqlite3.connect("DataBases/xp.db")
    cur = con.cursor()
    gid = guild.id
    cur.execute("""
        CREATE TABLE IF NOT EXISTS xp_roles (
            guild_id INTEGER PRIMARY KEY,
            data TEXT
        );
    """)

    cur.execute(f"SELECT * FROM xp_roles WHERE guild_id = {gid}")
    row = cur.fetchone()
    level = str(level)
    role = str(role)
    if not row:
        cur.execute(f"""
            INSERT INTO xp_roles (guild_id)
            VALUES ({gid});
        """)
        con.commit()
    if save:
        val = False
        cur.execute(f"SELECT data FROM xp_roles WHERE guild_id = {gid}")
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
        cur.execute(f"UPDATE xp_roles SET data = \"{str(data)}\" WHERE guild_id = {gid}")
        con.commit()
        con.close()
        return val
    else:
        cur.execute(f"SELECT data FROM xp_roles WHERE guild_id = {gid}")
        data = json.loads(cur.fetchone()[0].replace("'", '"'))
        if not level is None:
            data = data.get(level)
        con.close()
        return data
# </editor-fold>

# <editor-fold desc="settings.db">
def server_settings(save, guild, stype=None, value=None):
    con = sqlite3.connect("DataBases/settings.db")
    cur = con.cursor()
    guild_id = str(guild.id)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS server_settings (
            guild_id TEXT PRIMARY KEY,
            roles TEXT,
            prefix TEXT,
            casenum INTEGER
        );
    """)

    cur.execute("SELECT * FROM server_settings WHERE guild_id = ?", (guild_id,))
    row = cur.fetchone()

    if not row:
        cur.execute("""
            INSERT INTO server_settings (guild_id, roles, prefix, casenum)
            VALUES (?, '[]', ';;', 0);
        """, (guild_id,))
        con.commit()

    if save:

        if stype == "roles":
            cur.execute("SELECT roles FROM server_settings WHERE guild_id = ?", (guild_id,))
            roles = json.loads(cur.fetchone()[0])

            role = str(value)

            if role in roles:
                roles.remove(role)
                msg = f"Removed <@&{role}> from the server config."
            else:
                roles.append(role)
                msg = f"Added <@&{role}> to the server config."

            cur.execute("""
                UPDATE server_settings
                SET roles = ?
                WHERE guild_id = ?;
            """, (json.dumps(roles), guild_id))

            con.commit()
            con.close()
            return msg

        elif stype == "prefix":
            cur.execute("""
                UPDATE server_settings
                SET prefix = ?
                WHERE guild_id = ?;
            """, (value, guild_id))

            con.commit()
            con.close()
            return f"Your server configuration for bot prefix has been updated to \"{value}\"."
        elif stype == "casenum":
            cur.execute(f"""
                SELECT casenum FROM server_settings WHERE guild_id = '{guild_id}'""")
            num = cur.fetchone()[0]
            num += 1
            cur.execute(f"""
                UPDATE server_settings
                SET casenum = ?
                WHERE guild_id = ?;
            """, (num, guild_id))
            con.commit()
            con.close()
            return num
        else:
            return "fella..."
    else:
        cur.execute("""
            SELECT roles, prefix, casenum
            FROM server_settings
            WHERE guild_id = ?;
        """, (guild_id,))
        data = cur.fetchone()
        con.close()

        if stype == "roles":
            return json.loads(data[0])
        elif stype == "prefix":
            return data[1]
        elif stype == "casenum":
            return data[2]
        else:
            return {
                "roles": json.loads(data[0]),
                "prefix": data[1],
                "casenum": data[2],
            }

def user_settings(save, userid: int, setting, data=None):
    returnval = False
    con = sqlite3.connect("DataBases/settings.db")
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user INTEGER PRIMARY KEY,
            xpmessage INTEGER
        );
    """) # temp - 0 = off, 1 = on (server), 2 = on (dms)

    cur.execute(f"SELECT * FROM user_settings WHERE user = {userid}")
    row = cur.fetchone()

    if not row:
        cur.execute(f"""
            INSERT INTO user_settings (user, xpmessage)
            VALUES ({userid}, 1);
        """)
        con.commit()

    if save:
        if setting == "xpmessage":
            cur.execute(f"""
                        SELECT xpmessage
                        FROM user_settings
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
                        FROM user_settings
                        WHERE user = {userid}
            """)
            returnval = cur.fetchone()[0]
    con.close()
    return returnval

def server_channels(save, guild, channel, data=None):
    con = sqlite3.connect("DataBases/settings.db")
    cur = con.cursor()
    gid = guild.id

    cur.execute("""
        CREATE TABLE IF NOT EXISTS server_channels (
            guild_id INTEGER PRIMARY KEY,
            modlog INTEGER,
            member INTEGER,
            message INTEGER,
            channel INTEGER,
            role INTEGER,
            voice INTEGER
        );
    """)

    cur.execute(f"SELECT * FROM server_channels WHERE guild_id = {gid}")
    row = cur.fetchone()

    if not row:
        cur.execute(f"""
            INSERT INTO server_channels (guild_id, modlog, member, message, channel, role, voice)
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
                    voice = {data}
                WHERE guild_id = {gid};
            """)
            con.commit()
            con.close()
            return f"All events have been set to channel \"<#{data}>\""

        cur.execute(f"SELECT {channel} FROM server_channels WHERE guild_id = {gid}")
        current = cur.fetchone()[0]

        if current == data:
            cur.execute(f"""
                        UPDATE server_channels
                        SET {channel} = NULL
                        WHERE guild_id = {gid};
                """)
            msg = f"Deleted \"<#{data}>\" from the {channel} event server config."
        else:
            cur.execute(f"""
                        UPDATE server_channels
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
                    FROM server_channels
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
        else:
            return {
                "modlog": data[1],
                "member": data[2],
                "message": data[3],
                "channel": data[4],
                "role": data[5],
                "voice": data[6]
            }
# </editor-fold>

def webhooks(save, guild, data):
    # data format = (id, token, name, channel)
    con = sqlite3.connect("DataBases/webhooks.db")
    cur = con.cursor()
    gid = guild.id
    cur.execute(f"""
                SELECT name FROM sqlite_master
                WHERE type = 'table' AND name = '{gid}';
            """)

    if not cur.fetchone():
        cur.execute(f"""
                    CREATE TABLE '{gid}' (
                        id INTEGER PRIMARY KEY,
                        token TEXT,
                        channel INTEGER
                    );
                """)
        con.commit()

    if save:
        cur.execute(f"""
                INSERT INTO '{gid}' (
                    id, token, channel
                ) VALUES ({data[0]}, '{data[1]}', {data[2]})
        """)
        con.commit()
        con.close()
        return True
    else:
        cur.execute(f"""
                SELECT * FROM '{gid}' WHERE channel = {data[0]} AND id = {data[1]}
        """)
        data = cur.fetchone()
        if data:
            con.close()
            return data
        con.close()
        return False