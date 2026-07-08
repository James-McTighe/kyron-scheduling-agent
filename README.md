# kyron-scheduling-agent

# Overall goal
Create a backend using Flask that can recieve calls and schedule appointments
# Plan

## What I will include
### Flask Backend core architecture
- database schema
  - since they didn't specify, I should be good to use SQLite to simplify things
- core endpoints
  - GET /patients and POST /patients
  - GET slots (appointment times)
  - POST /appointments
  - GET /appointments/<patient_id>
- Protocol logic
Hardcode the routing rules from the PDF into backend lookup logic. For example, when checking GET /slots for a "New Patient" with a "Fracture," ensure the query filters out doctors who don't accept new patients or that specific issue.
### Conversational flow
- collect patient name / dob
- ask if they're a new or returning patient
- ask for a body part / injury type
- call api to fetch slots
- confirm booking and save to db
### Bare minimum front end
- Just render a list of calls directly fetched from a database table tracking the call logs
- Ensure it shows the transcript, the patient info, and the final booking status
### Simple Dockerized Deployment
- Set up a simple docker-compose.yml that spins up Flask app and frontend
- Deploy it to an AWS EC2 instance early so you aren't fighting deployment errors in the final hours

## What I won't have time for
- Complex Conversation Fallbacks & Interruptions: Don't spend hours trying to make the voice agent handle heavy conversational tangents or aggressive user interruptions. If they go off-script, let it fail or loop back gracefully, but don't over-engineer it.
- 100% Physician Protocol Edge Cases: Implement routing for 2 or 3 distinct doctors to prove code works, and state in the README that the data structure supports adding the rest seamlessly.
- Rescheduling and Cancellations
- Frontend Design / UI UX
- Authentication/User Accounts

***
# Final thoughts / report
### What I built
### Trades offs / limitations.  What I delibrately skipped
### What I would do with more time

