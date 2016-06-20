import cherrypy
import sqlite3 as sql
import os, os.path

#Name-bank.
db         = 'apd.db'
sockethost = '127.0.0.1'
socketport = 8080
filepath   = 'home/jorge/Documents/GitHub/d3-calendar/'
staticpath = filepath + 'public'

###[SQLITE BLOCK]###
#Store the DB connection in the thread_data container.
def connect(thread_index):
    cherrypy.thread_data.db = sql.connect(db)
    cherrypy.thread_data.db.isolation_level = None

#Establishes DB connection when new thread is started.
cherrypy.engine.subscribe('start_thread', connect)

#Alias functions for DB operations.
def commit():
    cherrypy.thread_data.db.commit()

def close():
    cherrypy.thread_data.db.close()

def writeData(file, headers, data):
    f = open(file + '.csv', 'w')

    #writes the headers
    line = (",").join(headers) + "\n"
    f.write(line)

    #writes the data rows
    for datum in data:
        line = (",").join( map(str,datum) ) + "\n"
        f.write(line)

    f.close()

###[CHERRYPY BLOCK]###
#Class for generating the web page object.
class Root(object):

    # Try localhost:8080/index?selection=DWI
    @cherrypy.expose
    def index(self, selection='ALL INCIDENTS'):
        cur = cherrypy.thread_data.db.cursor()

        f = open('selection.json', 'w').write('{"selection": "' +selection+ '"}')

        #incident type selector
        query = 'SELECT DISTINCT type FROM incident ORDER BY type'
        cur.execute(query)
        commit()

        params = cur.fetchall()

        writeData('types', ['type'], params)

        #aggregated data filtered by selection
        if selection == 'ALL INCIDENTS':
            query = '''SELECT date, count(id) AS total
                       FROM incident
                       WHERE date LIKE '%2016'
                       GROUP BY date'''
            cur.execute(query)
        else:
            query = '''SELECT date, count(id) AS total
                       FROM incident
                       WHERE date LIKE '%2016'
                         AND type = ?
                       GROUP BY date'''
            cur.execute(query, (selection,))
        commit()

        result = cur.fetchall()
        data = []

        for d in result:
            #changing format from mm/dd/yyyy to yyyy-mm-dd
            datestring = str(d[0])
            date = datestring[6:10]+ '-' +datestring[0:2]+ '-' +datestring[3:5]

            value = str(d[1])
            data.append([date, value])

        writeData("data", ["date", "crimes"], data)

        page = open("index.html", "r").read()
        return page

    @cherrypy.expose
    def shutdown(self):
        cherrypy.server.stop()
        cherrypy.engine.exit()
        return 'shutdown'

###[EXECUTION BLOCK]###
if __name__ == '__main__':
    #Establish a path for static content in the local directory.
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': ''
        }
    }
    #Set the app to listen on port <socketport> from the local address.
    #(The router must foward port 80 to the local address for external access.)
    cherrypy.config.update({'server.socket_host': sockethost,
                            'server.socket_port': socketport,
                           })
    #Start the app.
    cherrypy.quickstart(Root(), '/', conf)
