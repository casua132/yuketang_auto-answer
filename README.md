# Rain Classroom Assistant (Android Version)

This project is a modified version of [TrickyDeath/RainClassroomAssitant](https://github.com/TrickyDeath/RainClassroomAssitant). Since the original project does not have a license, this repository is for personal study and backup purposes only. All rights of the core logic belong to the original author.

# Project Description

This is an Android-compatible version of the Rain Classroom Assistant. It uses [Flet](https://flet.dev/) for the UI and can be run on Android devices.

## How to Run

~~### Method 1: Using Flet App on Android (Development)~~

~~1.  Install the **Flet** app from the Google Play Store (or App Store on iOS, though this is tailored for Android).~~
~~2.  Ensure your Android device and PC are on the same network.~~
~~3.  Run the server on your PC:~~
    ```bash
    flet run android_app/main.py --port 8550
    ```
~~4.  Open the Flet app on Android and enter the URL shown in your terminal (usually `http://<your-pc-ip>:8550`).~~

### Method 2: Build APK (Distribution)

To build a standalone APK, you need to install `flet` and set up the Flutter environment (which Flet uses under the hood).

1.  Install dependencies:
    ```bash
    pip install flet
    ```
2.  Run the build command:
    ```bash
    flet build apk --project android_app
    ```
    (Note: This requires a properly set up Flutter environment. Refer to Flet documentation for details).

## Features

-   **Mobile UI**: Redesigned interface for touch screens.
-   **Login**: Scan QR code to login via WeChat (same as desktop version).
-   **Auto-Answer**: Automatically answers questions using AI (requires API Key).
-   **Auto-Danmu**: Sends bullet comments automatically.
-   **Monitoring**: Monitors active classes and performs actions.

## Configuration

The configuration is stored in the app's data directory. You can adjust settings via the "配置" (Config) button in the app.

### API Key

To use the AI answering feature (Doubao model), you need to provide the `DOUBAO_API_KEY`.
Currently, you may need to add it to a `.env` file in the working directory or modify the code to input it.
(Note: The current implementation reads from environment variables. A future update will allow inputting it in the UI).

## Credits

Based on the original RainClassroomAssistant project.
