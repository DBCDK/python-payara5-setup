

### Examples

#### .app

 * location relative to current dir or absolute
 * context-root
 * application name
```
location = /tmp/foo.war
context-root = /
name = my-foo-app 
```
deploys `foo.war` at `/` with the name `my-foo-app`

#### .lib
 * Location (default common)
   * jar-location relative to current dir or absolute
```
postgresql.jar
[applibs]
my-special-logger.jar
```

installs `postgresql.jar` for container usage, and `my-...jar` for application use 

#### .cres
 * Property map
   * jndi-name
   * keys = values
```
[properties]
"jndi/my-props"
url = http://localhost/${CONTEXT_PATH}
```
creates a jndi resource `jndi/my-props` with properties `url` = `http://...`

 * String value
   * jndi-name = value
```
[string]
jndi/my-str = "The magic text"
```
creates jndi string resource `jndi/my-string` with value `The ...`

#### .set
 * ensure a xml node
```
[ensure]
'configs/config[@name="server-config"]'
. = mdb-container
max-pool-size = ${THREADS|2}
```
Ensures the node `\<configs>\<config name="server-config">\<mdb-container max-pool-size="...">` exists
 * attributes
```
[attributes]
'configs/config[@name="server-config"]/mdb-container'
max-pool-size = 1
```
Sets the property of the existing created node(s)

 * properties
```
[properties]
'configs/config[@name="server-config"]/network-config/protocols/protocol/http[@default-virtual-server="server"]'
serverName = "${SERVER_NAME|}"
scheme-mapping = "X-Forwarded-Proto"
```
Sets the `<property name="serverName" value="..."/>` in the `http` element

#### .sys

Sets system properties
```
my.system.property = my-valye

```

#### .jdbc

```
; "postgresql" # databasetemplate - postgresql is default
[jdbc/my-ds]
"user:pass@host:port/database"
non-transactional-connections = true
```
Create `jdbc/my-ds` as a nontransactional postgresql datasource to the address given address

#### .jms

 * enable remote jms-server
```
[REMOTE]
address = host.my.domain:7676
```
Configure remote JMS server 

 * Factory
```
[QueueConnectionFactory]
name = "jndi/my-factory" ; required
; transaction-support = XATransaction # this is default
```
Create a connection factory with the given name, and sane defaults. Properties are the `domain.xml` known properties.

 * Queue/Topic
```
[Queue]
name = "jndi/my-worker-queue" ; required
; AddressList = "host:port,host:port,..."
```
Create a queue for a mdb

#### .jvm

Set JVM options

```
[remove]
-Xmx*
-Xms*
[add]
-Xmx2G
-Xms2G
```

The above example removes any `-Xmx` or `-Xms` settings already in the options, and adds new.

A special section exists: `[clear]` that will remove all settings.

## Setup hint
 * run `payara5/bin/asadmin --verbose`
 * enter the page that allow the change wanted
 * copy domain.xml
 * execut change
 * `diff -u -w -W280 <(xmllint -format domain.xml | xmllint --exc-c14n -) <(xmllint -format payara5/glassfish/domains/domain1/config/domain.xml | xmllint --exc-c14n -)`
 * try to replicate by rmaking file(s) that modify `domain.xml`
 