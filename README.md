Example usage:
```Python
hub = get_hub("Mac address of ics2000", "email", "password")
```

This will also list the devices connected
```Python
hub.turnon(id of device to turn on)
  
hub.turnoff(id of device to turn off)

hub.getlampstatus(id of device)
```

Heavily WIP
