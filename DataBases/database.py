import sqlite3, discord

def modlog(save, interaction, data = None, user: discord.Member = None):
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
                timestamp TEXT
            );
        """)

    if save and data:
        cur.execute(f"""
            INSERT INTO "{guild_id}" (user, mod, reason, message, type, timestamp)
            VALUES (?, ?, ?, ?, ?, ?);
        """, data)
        con.commit()
        cur.execute(f"""
            SELECT * FROM '{guild_id}'
            WHERE user = '{str(data[0])}';
            """)
        msg = f"Successfully warned <@{data[0]}>, they now have {len(cur.fetchall())} modlogs!"
    else:
        cur.execute(f"""
            SELECT type, reason, message, timestamp, mod
            FROM '{guild_id}'
            WHERE user = '{user.id}'
            LIMIT 25;
        """)
        rows = cur.fetchall()
        msg = discord.Embed(color=discord.Color.dark_green())
        msg.set_author(name=user.name, icon_url=user.display_avatar.url)
        if not rows == []:
            amount = 0
            for row in rows:
                amount += 1
                msg.add_field(name=f"{amount}. {row[3]}", value=f"{row[0]} | \"{row[1]}\" | MSG: \"{row[2]}\" ~ <@{row[4]}>", inline=False)
            cur.execute(f"""
                SELECT type, reason, message, timestamp, mod
                FROM '{guild_id}'
                WHERE user = '{user.id}'
            """)
            rows = cur.fetchall()
            if len(rows) > 25:
                msg.description = (f"{user.mention} has {len(rows)} modlogs, only displaying the top 25.\n"
                                   f"-# *Why? Read [here](<https://www.pythondiscord.com/pages/guides/python-guides/discord-embed-limits/> \"A redirect to PythonDiscord\").*")
        else:
            msg.description = f"No modlogs found for {user.mention}!"
    con.close()
    return msg

def server_roles(save, interaction, role=None):
    con = sqlite3.connect("DataBases/role.db")
    cur = con.cursor()
    guild_id = str(interaction.guild.id)
    cur.execute(f"""
        SELECT name FROM sqlite_master
        WHERE type = 'table' AND name = '{guild_id}';
    """)
    if not cur.fetchone():
        cur.execute(f"""
            CREATE TABLE '{guild_id}' (
                roles TEXT
            );
        """)

    if save and role:
        cur.execute(f"""
            SELECT * FROM '{guild_id}' WHERE roles = ?;
        """, (str(role),))
        exists = cur.fetchone()

        if exists:
            cur.execute(f"""
                DELETE FROM '{guild_id}' WHERE roles = ?;
            """, (str(role),))
            msg = f"Removed <@&{role}> from the server config."
        else:
            cur.execute(f"""
                INSERT INTO '{guild_id}' (roles) VALUES (?);
            """, (str(role),))
            msg = f"Added <@&{role}> to the server config."
        con.commit()
        con.close()
        return msg
    cur.execute(f"SELECT roles FROM '{guild_id}'")
    rows = cur.fetchall()
    con.close()
    return [row[0] for row in rows]

def server_prefix(save, guild, prefix=None):
    con = sqlite3.connect("DataBases/prefix.db")
    cur = con.cursor()
    guild_id = str(guild.id)
    if save:
        cur.execute(f"""
                SELECT * FROM 'Main'
                WHERE guild_id = '{guild_id}';
            """)
        if not cur.fetchone():
            cur.execute(f"""
                    INSERT INTO 'Main' (guild_id) VALUES ('{guild_id}');
                    """)
        else:
            cur.execute(f"""
                    UPDATE Main
                    SET prefix = NULL
                    WHERE guild_id = '{guild_id}'
                      AND prefix IS NOT NULL;
                    """)
        cur.execute(f"""
                UPDATE 'Main'
                SET prefix = '{prefix}'
                WHERE guild_id = '{guild_id}';
                """)
        con.commit()
        con.close()
        return f"Your server configuration for bot prefix has been updated to \"{prefix}\"."
    else:
        cur.execute(f"""
                SELECT prefix FROM 'Main' WHERE guild_id = '{guild_id}';
                """)
        yeah = cur.fetchone()
        con.close()
        if yeah == None:
            return ";;"
        return yeah[0]