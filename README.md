# Quiz as a Service 

## General

This api provides the possiblity for registered creators 
to create, update and delete quizs, as well as observe the 
score and progress of participants.

Participants also need to be registered users, and are able to answer
questions, change the answers as well as see the progress of their quiz.



## API

General Endpoint: :host:/qaas/

### Quiz

#### GET quiz/

If authenticated as a a Creator one recieves a JSON of all the quiz created.

##### parameters search
with a search parameter one can search in the names of quizs and recieves all matching quizs

#### POST quiz/

to create a new quiz send a json payload with the name of the new quiz. The response
will contain a serialised representation of the new quiz.

#### DELETE quiz/<int:quizid>

this deletes a quiz according to his id/private_key

#### UPDATE quiz/<int:quizid>

this updates a quiz matching the id. This is mainly to change the name of the quiz

### Question

#### GET question/

returns a list of all the created questions belonging to quizzes the
authenticated users is the creator of

#### POST question/

creates a new question, a questions always needs:
{ "text": The text of the question (string) ,
  "quiz": The pk of the quiz it belongs to (int) }

#### DELETE question/<int:questionid>
deletes a question

#### UPDATE question/<int:questionid>
changes a questions selected by pk according to the payload

### Answer

#### GET answer/
returns all the answers of all the questions belong to all the quizes one is the creator of

#### POST answer/

creates a new answers: 
payload = {
    "question": The question id (int),
    "text": The quetsion text (string),
    "isCorrect": if the answers is true or false (boolean)
}
#### GET answer/<int:questionid>

returns all the answers belong to a question

#### DELETE answer/<int:answerid>

#### UPDATE answer/<int:answerid>

### Participating in a Quiz

#### GET participate/quiz

returns all the quizs one is invite to participate in

##### PARAMS search
returns all quizs where name matches the query


#### POST participate/quiz/<int:quizid>/question/<int:questionid>/selectedanswer/<int:answerid>

answers a particular question of a quiz with a chosen answer

#### UPDATE participate/quiz/<int:quizid>/question/<int:questionid>/selectedanswer/<int:answerid>

changes the answers of the question (selected by id) from the quiz to another answer


### Progress

#### GET progress/<int:quizid>

returns the progress of the quiz one as a participant is participating in

#### GET participations/<int:participationid>/score

as a creator returns the score of a given participation (participation is a Participant and a Quiz)

#### GET participations/<int:participationid>/progress

as a creator returns the score of a given participation (participation is a Participant and a Quiz)

### POST invitations/new/<str:email>/<int:quizid>

invite someone per email to a new quizs, will automatically invite unregistered emails to
create an account

### GET invitations/
lists all the quizs a participant has been invited too

### POST invitations/<int:invitationid>

accept an invitation


### POST notify-results/<int:participationid>'

send an email to the quiz user of the participation with the results

# Daily Usage Report

To download the usage report of today be authenticated as staff and 
access 
#### GET todaysussage/

