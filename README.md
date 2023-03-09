# 
This is the mediawiki to describe the QPTDat ontology and gather community feedback. 


## MediaWiki Installation
1. Comment LocalSetting.php file in `docker-compose.yml` file.
2. Start infrastructure
```
docker-compose up -d
```
3. Set up Mediawiki by going to http://qptdat.plasma-mds.org/wiki and following the wizard.
    * Database must be `ontology_wiki_database_1`
    * Make sure to install SemanticMediaWiki
4. Put `LocalSetting.php` file in root directory of this project.
5. Change `$wgServer` variable in `LocalSetting.php` to `$wgServer = "http://qptdat.plasma-mds.org/wiki";`
6. Uncomment LocalSetting.php
7. Restart mediawiki
8. Run interactive bash to update mediawiki
```
docker exec -it ontology_wiki_mediawiki_1 bash
```
    * In container run
    ```
    maintenance/update.php
    ```
### Create a pywikibot configuration file for the new wiki
1. Look up where the pywikibot scripts are stored (`pip show pywikibot`) and change the both of the following commands to your path.
2. Run the set up script with the following script:
```
python ${pywikibotLocation}/scripts/generate_family_file.py
```
3. Follow the configuration wizard.

### Create a bot account on the new wiki
1. Create on `http://qptdat.plasma-mds.org/wiki/index.php/Special:BotPasswords` a bot by giving a name and saving the password.

### Add bot configuration
1. Generate the required pywikibot configuration
```
python ${pywikibotLocation}/scripts/generate_user_files.py
```
2. Optional: Decrease the sleep time for save action by adding `put_throttle = 1` to the `user-config.py` file.

# Load pyLODE results into SMW

```
./createWiki.py -p "resource/*.ttl"
```
# Create plain HTML Documentation
Run the python script on a pattern matching all files that should be documented. 
```
./createHTML.py -p "resource/*.ttl"
```




