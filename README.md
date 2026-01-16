# HOURX - Modern Time Bartering Platform

HourX has been fully updated with a verified modern UI featuring glassmorphism, smooth animations, and a responsive design.

## Features
- **Modern Dashboard**: Track your time credits with a beautiful gradient card interface.
- **Skill Marketplace**: Discover skills in a grid layout with vibrant cards.
- **Barter System**: Request services, lock hours in escrow, and release them upon completion.
- **Profiles**: manage your identity and see your reputation.

## Deployment / Source Code
The project is version controlled and hosted on GitHub:
- **Repository**: [https://github.com/Tusarkanta-07/hourx.git](https://github.com/Tusarkanta-07/hourx.git)
- **Branch**: `main`

## How to Run

1. **Start the Server** (if not already running)
   ```bash
   cd hourx
   py manage.py runserver
   ```

2. **Access the Application**
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## User Flow
1. **Register**: Create an account via the modern signup form.
2. **Offer Skill**: Go to "Offer a Skill" from the dashboard to list what you can do.
3. **Request**: Browse the Marketplace, click "Details", then "Request Service".
4. **Accept**: Receiver checks "Inbox" (Received Requests) to accept. *Hours are locked.*
5. **Complete**: Sender (or appropriate party) marks as "Complete" in "Sent Requests". *Hours are transferred.*

## Design System
- **Fonts**: Outfit (Body) & Plus Jakarta Sans (Headings).
- **Colors**: Indigo/Violet Primary Gradient.
- **Effects**: Glassmorphism, Fade-in animations, Hover lifts.
