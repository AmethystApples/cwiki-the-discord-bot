<h2>Cwiki</h2>
Cwiki is meant to be a quick-and-easy customizable wiki you can access through Discord. You can save server-wide definitions for inside jokes, OC characters, and much more! Terms may have multiple definitions from different, but users can rank them thanks to our wook-and-book voting system.

<h4>Overview</h4>
The quick-wiki discord bot! With Cwiki, you can create, retrieve, and rank server-specific entries of any topic. To get started, use /help. 
<h4>Installation</h4>

```bash
pip install discord.py
pip install python-dotenv
pip install MySQL 
pip install transformers
```

<h4>Commands</h4>
<h6>/entry</h6>
Adds a new word and its definition to the database. Usage: /entry word:<term> definition:<definition>
<h6>/define</h6>
Retrieves a collection of definitions for a specified term. Usage: /define word:<term>
<!--<h6>/summarize</h6>
Generates a summary of definitions for a specified term using AI. Usage: /summarize word:<term>-->
<h6>/help</h6>
Provides a tutorial on how to use the bot's commands.
<h4>Wooking</h4>
Users can vote on entries by accessing their definitions and clicking the 📈 and 📉 buttons to add or subtract 'wooks'. Wooks are Cwiki’s point system for ranking definitions.
    
<!--<h4>Credits</h4>

This bot uses the pre-trained **[BART model](https://github.com/facebookresearch/fairseq/tree/main/examples/bart)** for its summarization feature.-->
