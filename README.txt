# Faction Crime Tracker - Readme

## What This Tool Does

This tool helps faction leaders or officers track the number of crimes committed by participating faction members over a period. You can use this information to run competitions or just monitor activity.

It uses a simple menu in a command window, so you don't need to type complex commands after the initial setup.

## Files Included

You should have these files in the **same folder**:

1.  `faction_crime_tracker.py`: The main program code. You don't need to run this directly.
2.  `requirements.txt`: A small file listing extra code the main program needs (specifically, the `requests` library for talking to the Torn API).
3.  `run_tracker.bat`: A helper file you will double-click to easily start the tracker. It handles installing needed extras and running the main program.
4.  `README.txt` (or `README.md`): This file you are reading now.

**Important:** When you run the tracker for the first time, another file will be created:

5.  `faction_data.db`: This is the **database file**. It stores ALL your member information (User ID, API Keys, Names) and their recorded crime statistics. **Do NOT delete this file unless you want to lose all tracked data and start over!** Keep this file safe.

## Setup Instructions (Only needs to be done once)

Follow these steps carefully:

**Step 1: Get the Files Ready**
*   Make sure all the files listed above (`faction_crime_tracker.py`, `requirements.txt`, `run_tracker.bat`, and this Readme) are downloaded and saved together in **one single folder** on your computer. You can create a new folder for this, perhaps named "Torn Crime Tracker".

**Step 2: Install Python (If you don't have it)**
*   This tool is written in Python, so you need Python installed on your computer. If you don't have it, or aren't sure, it's best to install it.
*   Go to the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/)
*   Download the latest stable version for Windows (usually a big button on the page).
*   Run the installer you downloaded.
*   **!! VERY IMPORTANT !!** During the installation, you will see a screen with checkboxes. Make sure you **check the box** that says something like:
    *   `Add Python 3.x to PATH`
    *   `Add python.exe to PATH`
    *   *(The exact wording might vary slightly depending on the version)*
    *   **Why?** Checking this box allows the `run_tracker.bat` file to find and use Python automatically. If you miss this step, the tracker won't start.
*   Continue through the rest of the installation using the default options (usually clicking "Install Now" is fine).
*   After installation is complete, it's sometimes a good idea to **restart your computer** to make sure Windows recognizes the new PATH setting.

**Step 3: Verify Files**
*   Just double-check that `faction_crime_tracker.py`, `requirements.txt`, and `run_tracker.bat` are all sitting together in the same folder.

## How to Run the Tracker

You **do not** need to run the `.py` file directly.

1.  Go to the folder where you saved the files.
2.  Find the file named `run_tracker.bat`.
3.  **Double-click `run_tracker.bat`**.
4.  A black command window will open. It will:
    *   Check if Python is installed correctly.
    *   Check if `pip` (Python's package installer) is working.
    *   Automatically install or update the necessary `requests` library (it might download something briefly the first time).
    *   If everything is okay, it will say "Starting Faction Crime Tracker..." and then you will see the main menu of the tracker program inside that window.

## Using the Tracker (The Menu)

Once the tracker starts, you will see a menu with numbered options:

*   **1. Add / Update Member:** Use this to add a new player to the tracker or change the API key or name of an existing player. You will be asked for their Torn User ID and their Torn API Key.
*   **2. Remove Member:** Use this to completely remove a player and their stats from the tracker (e.g., if they leave the faction or competition).
*   **3. List All Members (and Edit/Delete):** Shows everyone currently being tracked. After the list appears, you'll have the option to type a User ID from the list to quickly Edit their details or Delete them.
*   **4. Update All Member Stats (Fetch from API):** This is the **most important** action for tracking. You need to run this periodically (e.g., at the start of your tracking period, and again at the end). It contacts the Torn servers (using the API keys you provided) to get the *current* crime count for *everyone* in the tracker. It saves this number and the time.
*   **5. Show Crime Results (Since Last Update):** After you have run option `4` at least *twice*, use this option to see the scores. It calculates the difference between the *last two times* you ran option `4` and shows you a ranked list of who did the most crimes in that period.
*   **0. Exit:** Closes the tracker program.

Just type the number corresponding to the action you want to perform and press Enter. Follow the prompts on the screen.

## Important Notes

*   **The Database (`faction_data.db`):** As mentioned, this file stores all your data. It's created automatically in the same folder. **Back it up if you are worried about losing data.** If you delete it, the tracker will start completely fresh next time.
*   **API KEYS ARE SENSITIVE:**
    *   You need to collect API keys from your participating members.
    *   These keys are stored inside the `faction_data.db` file on your computer.
    *   Anyone who gets access to this file could potentially see the API keys. Keep the folder and the `.db` file reasonably secure.
    *   **MOST IMPORTANTLY:** Tell your members to **ONLY** give you a **LIMITED ACCESS** API key. They should create a new key specifically for this tracker.

## How Members Create the RIGHT API Key

Instruct your members to do the following in Torn:

1.  Go to **Preferences** (usually under your user icon/name).
2.  Go to the **API Keys** section.
3.  Click **Create API Key**.
4.  Give the key a descriptive **Name** (like "Faction Crime Tracker").
5.  Select **Limited Access Key**. This is crucial!
6.  A list of categories will appear (Global, User, Faction, Torn, etc.). Find the **User** category.
7.  Under **User**, find the **`crimes`** checkbox and **check ONLY that box**. (It might automatically check `basic` under `Public access`, which is usually fine, but the essential part is *only* `crimes` under `User`).
8.  Leave **ALL OTHER** boxes **unchecked**, especially things related to attacks, items, money, etc.
9.  Click **Create**.
10. Copy the generated API key string and give it to you (the person running the tracker).

By using a limited key with only `crimes` access, members ensure you can only read their total crime count and nothing else, which is much safer for everyone.

## Basic Troubleshooting

*   **Error: "Python not found" or "'python' is not recognized..."**:
    *   This almost always means Python wasn't installed correctly *or* the "Add Python to PATH" box was NOT checked during installation.
    *   Try reinstalling Python carefully, making absolutely sure you check the "Add to PATH" box. You might need to restart your computer afterwards.
*   **Error: "Failed to install required Python libraries"**:
    *   Check your internet connection. The script needs internet access to download the `requests` library the first time.
    *   Try running the `run_tracker.bat` again.
    *   If it consistently fails, you *might* have a permissions issue. Try right-clicking `run_tracker.bat` and choosing "Run as administrator", BUT only do this if the normal way fails repeatedly, as it's usually not necessary.
*   **Tracker menu doesn't appear after running `.bat`**: Look for error messages in the black window. They might give a clue about what went wrong (like a problem finding Python or installing libraries).

---

Good luck with your faction tracking!