# Lab Instructions

Lab instructions may contain three types of information:

* Screen (UI) interactions 
* Text commands
* Dialog Close

#### Keyboard or Mouse Action

When a keyboard or mouse action is required, the text will include a box with the instructions.

!!! abstract "Select the Infrastructure Icon in the watsonx.data UI"

#### Command Text

Any text that needs to be typed into the system will be outlined in a grey box. 

!!! abstract "Enter this text into the SQL window and Run the code"

    ```
    SELECT
      *
    FROM
      "hive_data"."ontime"."ontime"
    LIMIT
      10;
    ``` 

A copy icon is usually found on the far right-hand side of the command box. Use this to copy the text and paste it into your dialog or command window. You can also select the text and copy it that way. Once you have copied the text, paste the value into the appropriate dialog using the paste command or menu.

!!! warning "Cut and Paste Considerations"

      * Some commands may span multiple lines, so make sure you copy everything in the box if you are not using the copy button.
      * Commands pasted into a terminal window will require that you hit the `Return` or `Enter` key for the command to be executed.
      * Commands pasted into a Presto CLI window will execute automatically.

#### Dialog Close 

There are instructions that will tell you to close the current dialog.

!!! abstract "Close the dialog by pressing the [x] in the corner"

In many cases you will also be able to use the Escape key to close the current window.

### Icon Reference

There are certain menu icons that are referred to throughout the lab that have specific names:

* Hamburger menu <span style="font-style:bold; color:blue;">&equiv;</span>
  
     This icon is used to display menu items that a user would select from.

* Kebab menu <span style="font-style:bold; color:blue;">&vellip;</span>

     This icon is usually used to indicate that there are specific actions that can be performed against an object.

* Twisty <span style="font-style:bold; color:blue;">&#9658;</span> and <span style="font-style:bold; color:blue;">&#9660;</span>

     Used to expand and collapse lists.
  
### URL Conventions

Your TechZone reservation contains a number of URLs for the services provided in the watsonx.data server. The URL will contain the name of the server and the corresponding port number for the service. Throughout the documentation, the server name will be referred to as <tt style="font-size: large; color: darkgreen;">region.services.cloud.techzone.ibm.com</tt> and port number is referred to as <tt style="font-size: large; color: darkgreen;">port</tt>. Where you see these URLs, replace them with the values found in your reservation.