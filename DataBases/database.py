import sqlite3

def warnings(save, interaction, data = None):
    msg = None
    con = sqlite3.connect("DataBases/warnings.db")
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
                timestamp TEXT
            );
        """)

    if save and data:
        cur.execute(f"""
            INSERT INTO "{guild_id}" (user, mod, reason, message, timestamp)
            VALUES (?, ?, ?, ?, ?);
        """, data)
        cur.execute(f"""
            SELECT * FROM '{guild_id}'
            WHERE user = '{str(data[0])}';
            """)
        msg = f"Successfully warned <@{data[0]}>, they now have {len(cur.fetchall())} warnings!"

    con.commit()
    con.close()

    return msg

def server_settings(save, interaction, role = None):
    msg = None
    con = sqlite3.connect("DataBases/serverconfigs.db")
    cur = con.cursor()
    guild_id = str(interaction.guild.id)
    cur.execute(f"""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = '{guild_id}';
                """,)

    if not cur.fetchone():
        cur.execute(f"""
                CREATE TABLE '{guild_id}' (
                    roles TEXT
                );
            """)

    if save:
        cur.execute(f"""
            SELECT *
            FROM '{guild_id}'
            WHERE roles = '{role}'
            """)
        if cur.fetchone():
            cur.execute(f"""DELETE FROM '{guild_id}' WHERE roles = '{role}';""")
            msg = f"Successfully deleted <@&{role}> from the server configuration!"
        else:
            cur.execute(f"""
                INSERT INTO '{guild_id}'(roles)
                VALUES ({role});
                """)
            msg = f"Successfully added <@&{role}> to the server configuration!"

    else:
        cur.execute(f"""
            SELECT * FROM '{guild_id}'
            """)

    con.commit()
    con.close()
    return msg