IBM MQ Extension

Parse the source code and identify instances of Producers, Consumers and the Queues and create objects.

Create links between Producers and Consumers based on the Queue through which they are connected with.
 
For resolving the queue name if it is declared as a variable then resolve it within the method. If not present within the method then search within the class.

Limitations:

String resolution for the Queue name happens only when present within the method or as a class. Else an object is created for the variable in which queue name would be stored.



