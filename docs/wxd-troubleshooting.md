# Troubleshooting watsonx.data

Although we have tried to make the lab as error-free as possible, occasionally things will go wrong. Here is a list of common questions, problems, and potential solutions.

   * [What are the passwords for the services](#what-are-the-passwords-for-the-services)
   * [A SQL Statement failed but there are no error messages](#a-sql-statement-failed-but-there-are-no-error-messages)
   * [Apache Superset isn't Starting](#apache-superset-isnt-starting)
   * [Apache Superset screens differ from the lab](#apache-superset-screens-differ-from-the-lab)
   * [Too many incorrect logins using VNC and now I'm blocked](#too-many-incorrect-logins-using-vnc-and-now-im-blocked-from-connecting)
   * [Presto doesn't appear to be working](#presto-doesnt-appear-to-be-working)
   * [Displaying Db2 Schema is failing](#displaying-db2-schema-is-failing)
   * [Queries are failing with a 400 code](#queries-are-failing-with-a-400-code)
   * [Queries are failing with a 200 or 500 code](#queries-are-failing-with-a-200-or-500-code)
   * [Queries are failing with memory errors](#queries-fail-become-of-insufficient-memory)
   * [SSH, VNC and watsonx.data UI are not working](#ssh-vnc-and-watsonxdata-ui-are-not-working)

   * [No access to Presto/Minio UI after restart](#no-access-to-prestominio-ui-after-restart)
   * [Firefox and Chrome freeze when connecting to MinIO](#firefox-and-chrome-freeze-when-connecting-to-minio)

### What are the passwords for the services?

See the section on [Passwords](wxd-reference-passwords#passwords).

You can get all passwords for the system when you are logged in as the <code style="color:blue;font-size:medium;">watsonx</code> user by using the following command.

!!! abstract ""
    ```bash
    cat /certs/passwords
    ```

You can also use the Jupyter notebook link to display the userids and passwords for the services.

### A SQL Statement failed, but there are no error messages

You need to use the Presto console and search for the SQL statement. Click on the Query ID to find more details of the statement execution and scroll to the bottom of the web page to see any error details. 

### Apache Superset isn't Starting

If Superset doesn't start for some reason, you will need to reset it completely to try it again. First make sure you are connected as the `watsonx` user **not** `root`.

Make sure you have stopped the terminal session that is running Apache Superset. Next remove the Apache Superset directory.

!!! abstract ""
    ```bash
    sudo rm -rf /home/watsonx/superset
    ```

We remove the docker images associated with Apache Superset. If no containers or volumes exist you will get an error message.

!!! abstract ""
    ```bash
    docker ps -a -q --filter "name=superset" | xargs docker container rm --force
    docker volume list -q  --filter "name=superset" | xargs docker volume rm --force
    ```

Download the superset code again.

!!! abstract ""
    ```bash
    git clone https://github.com/apache/superset.git
    ```

The `docker-compose-non-dev.yml` file needs to be updated so that Apache Superset can access the same network that watsonx.data is using. 

!!! abstract ""
    ```bash
    cd ./superset
    cp docker-compose-non-dev.yml docker-compose-non-dev-backup.yml

    sed '/version: "3.7"/q' docker-compose-non-dev.yml > yamlfix.txt
    cat <<EOF >> yamlfix.txt
    networks:
      default:
        external: True
        name: ibm-lh-network
    EOF
    sed -e '1,/version: "3.7"/ d' docker-compose-non-dev.yml  >> yamlfix.txt
    ```

We update the Apache Superset code to version `2.1.0`.

!!! abstract ""
    ```bash
    sed 's/\${TAG:-latest-dev}/2.1.0/' yamlfix.txt > docker-compose-non-dev.yml
    ```

Use docker-compose to start Apache Superset.

!!! abstract ""
    ```bash
    nohup docker compose -f docker-compose-non-dev.yml up &
    ```

The `nohup` command will issue a message indicating that output will be directed to the `nohup.out` file. It takes some time for the service to start, so be patient! You can view any output from the Apache Superset system by viewing the `nohup.out` file in the directory where you installed superset.

### Apache Superset screens differ from the lab

The Apache Superset project makes frequent changes to the types of charts that are available. In some cases they remove or merge charts. Since these charts changes are dynamic, we are not able to guarantee that our examples will look the same as what you might have on your system.

### Presto doesn't appear to be working

If you find that the watsonx.data UI is generating error messages that suggest that queries are not running, or that the Presto service is dead, you can force a soft restart of Presto with the following command:

!!! abstract ""
    ```
    docker restart ibm-lh-presto
    ```

This will restart the Presto server. If you find that does not fix your problem, you will need to do a hard reset using the following commands:

!!! abstract ""
    ```
    sudo su -
    cd /root/ibm-lh-dev/bin
    ./stop_service ibm-lh-presto
    export LH_RUN_MODE=diag
    ./start_service ibm-lh-presto
    check-presto
    ```
The command will wait until the service is running before exiting.

### Displaying Db2 Schema is failing

Occasionally when attempting to expand the Db2 catalog (schema), the watsonx.data UI will not display any data or issue an error message. You can try refreshing the browser (not the refresh icon inside the UI) and try again. If you find that this is failing again, open the Query workspace and run the following SQL (replace db2_gosales with the name you cataloged the database with).

!!! abstract ""
    ```sql
    select count(*) from db2_gosales.gosalesdw.go_org_dim 
    ```

The result should be `123` and hopefully the tables that are part of the schema will display for you. 

### Queries are failing with a 400 code

The watsonx.data UI will log you out after a period of inactivity, but doesn't tell you that this has happened. When you attempt to run a query, the error that is returned (400) indicates that you need to log back in again.

### Queries are failing with a 200 or 500 code

A 500 code may indicate the watsonx.data UI has a problem connecting with the Presto engine. First log out of the console and trying logging back on. If that fails to solve the problem, you will need to reboot the console. Open up a terminal window into the server:

As the root user, restart the docker container that is running the watsonx.data UI.

!!! abstract ""
    ```bash
    docker restart lhconsole-nodeclient-svc
    ```

### Queries fail become of insufficient memory

If you are running a complex query, you may get an error message similar to "Query exceeded per-node user memory limit" or a something similar. Watsonx.data (Presto) attempts to limit the amount of resources being using in a query and will stop a query if it exceeds a certain threshold. 

You can change the behavior of the system by making the following changes. 

!!! error "During this step you will disconnect anyone running a query on the server."

What you need to do is make a change to the configuration settings of the Presto engine. As the root user, enter the docker container for the presto engine:

!!! abstract ""
    ```bash
    docker exec -it ibm-lh-presto /bin/bash
    ```

Next, copy the original config file to a safe place in case we make an error:

!!! abstract ""
    ```bash
    cp /opt/presto/etc/config.properties /opt/presto/etc/config.properties.backup
    ```

Then update the properties file.

!!! abstract ""
    ```bash
    cat >> /opt/presto/etc/config.properties << EOL
    experimental.spiller-spill-path=/tmp
    experimental.spiller-max-used-space-threshold=0.7
    experimental.max-spill-per-node=10GB
    experimental.query-max-spill-per-node=10GB
    experimental.spill-enabled=true
    query.max-memory=10GB
    query.max-memory-per-node=10GB
    query.max-total-memory-per-node=10GB
    query.max-total-memory=10GB
    EOL
    ```

Doublecheck that it worked.

!!! abstract ""
    ```bash
    cat /opt/presto/etc/config.properties | grep experimental
    ```

<pre style="font-size: small; color: darkgreen; overflow: auto">
experimental.max-spill-per-node=10GB
experimental.query-max-spill-per-node=10GB
experimental.spill-enabled=true
experimental.spiller-max-used-space-threshold=0.7
experimental.spiller-spill-path=/tmp
</pre>

If it is all good then exit the container.

!!! abstract ""
    ```bash
    exit
    ```

And now we restart the container. Make sure that you don't impact other users!
!!! abstract ""
    ```bash
    docker restart ibm-lh-presto
    ```
Now try running your query again. 

!!! note "Once you make this change, only restart presto using the above command, otherwise you will lose the changes."

### SSH, VNC and watsonx.data UI are not working

Symptoms:

* You've tried to use SSH to log into the system, and you get a timeout error.
* All the Web-based UIs (watsonx.data UI, Presto) fail.

Find your email message that contains details of your reservation. Details of what the reservations and the page containing details of the reservation can be found in the [Accessing the reservation](wxd-reference-access.md) section. 

Once the details appear, scroll down to the bottom of the web page, and you will see the VM Remote Console button.

![Browser](wxd-images/techzone-vpn.png)

You can access the logon screen of the virtual machine by pressing the VM Remote Console button. 

![Browser](wxd-images/techzone-console.png)

Clicking on this button will display the logon screen for the server.

![Browser](wxd-images/techzone-guacamole.png)

If you see this screen, the system is running and there is something wrong the watsonx.data service (see instructions below).

If you see the following screen:

![Browser](wxd-images/desktop-poweroff.png)

This means your server has been turned off. Click on the Power on button.

![Browser](wxd-images/desktop-poweronyes.png)

Make sure to press the Yes button to turn the power on! In a few minutes you should see the logon screen again.

![Browser](wxd-images/techzone-guacamole.png)

Wait for a few minutes for all the services to start, and then you will be able to use SSH, VNC, and watsonx.data UI.

### Reset watsonx.data

If you can log into the watsonx userid using the VM Remove console, you can reset the watsonx.data server with the following steps.

SSH into the server as the root user. Then switch to the development code bin directory.

!!! abstract ""
    ```bash
    cd /root/ibm-lh-dev/bin
    ```

Check the status of the system with the following command.
!!! abstract ""
    ```bash
    ./status.sh --all
    ```

Output will look similar to:
<pre style="font-size: small; color: darkgreen; overflow: scroll"">
using /root/ibm-lh-dev/localstorage/volumes as data root directory for user: root/1001 
infra config location is /root/ibm-lh-dev/localstorage/volumes/infra
lhconsole-ui              running   0.0.0.0:9443->8443/tcp, :::9443->8443/tcp
lhconsole-nodeclient-svc  running   3001/tcp
lhconsole-javaapi-svc     running   8090/tcp
lhconsole-api             running   3333/tcp, 8081/tcp
ibm-lh-presto             running   0.0.0.0:8443->8443/tcp, :::8443->8443/tcp
ibm-lh-hive-metastore     running		
ibm-lh-postgres           running   5432/tcp
ibm-lh-minio              running			
</pre>

If the any of the services are not running, you will need to restart the system with the following set of commands.
!!! abstract ""
    ```bash
    cd /root/ibm-lh-dev/bin
    ./stop-milvus
    ./stop
    export LH_RUN_MODE=diag
    ./start
    ./start-milvus 
    ```

Wait for all services to start and then check to see if you can connect to the watsonx.data UI. 

### No access to Presto/Minio UI after restart

If you are using a TechZone image that has been suspended, or restarted, you may come across a situation where you are unable to connect to any service that uses the `http` protocol. The `watsonx.service` needs to have a diagnostic flag set that opens up these ports, and sometimes this diagnostic setting is not being updated. 

To manually stop and start the system, you will need to connect with root user privileges and run the following commands:

!!! abstract ""
    ```bash
    cd /root/ibm-lh-dev/bin
    ./stop-milvus
    ./stop
    export LH_RUN_MODE=diag
    ./start
    ./start-milvus 
    ```

This set of commands will stop all the services in watsonx.data and restart them in diagnostic mode. This will now open the `http` ports for use.

### Firefox and Chrome freeze when connecting to MinIO

Firefox and Chrome on OSX will occasionally freeze when connecting to the MinIO console. The Safari browser is much more reliable. This problem appears to be caused by some features which are not properly handled by these browsers. 

