import sqlite3

def warnings(save, interaction, data = None):
    msg = None
    con = sqlite3.connect("DataBases/warnings.db")
    cur = con.cursor()

    cur.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name = ?;
                """, (str(interaction.guild_id),))

    if not cur.fetchone():
        cur.execute(f"""
            CREATE TABLE '{str(interaction.guild_id)}' (
                user TEXT,
                mod TEXT,
                reason TEXT,
                message TEXT,
                timestamp TEXT
            );
        """)

    if save and data:
        cur.execute(f"""
            INSERT INTO "{str(interaction.guild_id)}" (user, mod, reason, message, timestamp)
            VALUES (?, ?, ?, ?, ?);
        """, data)
        cur.execute(f"""
            SELECT * FROM '{str(interaction.guild_id)}'
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

    cur.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name = ?;
                """, (str(interaction.guild_id),))

    if not cur.fetchone():
        cur.execute(f"""
                CREATE TABLE '{str(interaction.guild_id)}' (
                    roles TEXT,
                );
            """)

    if save:
        cur.execute(f"""
            INSERT INTO "{str(interaction.guild_id)}" (roles)
            VALUES (role);
            """)

    else:
        cur.execute(f"""
            SELECT * FROM '{str(interaction.guild_id)}'
            """)
        msg = cur.fetchall()

    con.commit()
    con.close()
    return msg