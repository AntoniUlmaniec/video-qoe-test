# Video QoE Assessment Platform

## About the Project
This project is a web application built with Streamlit, designed to conduct subjective Quality of Experience (QoE) video assessments. The platform was developed in accordance with research methodologies to ensure 
that the participant's internet connection quality does not affect the video playback smoothness, providing accurate and reliable test results.

## Key Features
* Download-then-Play Mechanism: A custom JavaScript/HTML video player that forces the file to be 100% downloaded into the browser's cache before playback is allowed. This guarantees zero network buffering or lag during the evaluation process.
* Training Phase: Includes a mandatory training phase (2 videos) to familiarize users with the process. The results from this phase are excluded from the final analysis, following ITU-T recommendations.
* Cloudflare R2 Hosting: Utilizes Cloudflare R2 storage to serve heavy video files efficiently with zero egress fees.
* Google Sheets Backend: Automatically records user demographic data and Mean Opinion Score (MOS) evaluations in real-time directly to Google Sheets.
* Responsive Design: Fully optimized for both mobile and desktop devices.

## Tech Stack
* Python (Streamlit)
* JavaScript / HTML5 (Custom Video Player integration)
* Cloudflare R2 (Video Hosting)
* Google Sheets API (Data Storage)

## https://video-qoe-test-cr4kqtcofajchzdjtt7p8q.streamlit.app
