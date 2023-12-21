# REST api Project
This project is designed to explain the relationship between non-user entities and user entities in order to understand the REST API, and to effectively acquire skills to handle cloud systems and databases in the future by distributing the project to GCP. Many companies are dealing with cloud systems such as GCP, AWS, and Azure, and these projects will be one way to properly convey my current REST API-based knowledge to future employers.

## Objective
- Use status codes appropriately and process client requests through Method and PATH

- Perform CRUD operations on data requested by the client using the GCP firebase database

- Understand the Python Flask web library and deploy the project through the GCP console

- Understand the relationships between user and non-user entities, and be able to handle non-user and user requests differently

- Establish relationships between non-user entities and perform CRUD operations

- Understand the user access code and token issuance flow through Auth0 and verify JWT

- Through Auth0, users can log in and sign up for distributed web applications
 
-  User requests can be properly performed through Postman, and the body and header of the request are distinguished, the header contents are accessed, Accept and Content-type are appropriately performed, and a status code is returned

## Instructions
1. An entity to model the user
2. At least two other non-user entities
3. The two non-user entities need to be related to each other
4. The user needs to be related to at least one of the non-user entities
5. Resources corresponding to the non-user entity related to the user must be protected

## For Non-User Entities
1. For each entity a collection URL must be provided that is represented by the collection name. 
   - E.g., GET /boats represents the boats collection
     
2. If an entity is related to a user, then the collection URL must show only those entities in the collection which are related to the user corresponding to the valid JWT provided in the request
   - E.g., if each boat is owned by a user, then GET /boats should only show those entities that are owned by the user who is authenticated by the JWT supplied in the request
    
3. For an entity that is not related to users, the collection URL should show all the entities in the collection.

4. The collection URL for an entity must implement pagination showing 5 entities at a time
   - At a minimum it must have a 'next' link on every page except the last
   - The collection must include a property that indicates how many total items are in the collection
    
5. Every representation of an entity must have a 'self' link pointing to the canonical representation of that entity
   - This must be a full URL, not relative path
    
6. Each entity must have at least 3 properties of its own.
   - id and self are not consider a property in this count.
   - Properties to model related entities are also not considered a property in this count.
    * E.g., a boat is not a property of a load in this count, and neither is the owner of a boat.
   - Properties that correspond to creation date and last modified date will be considered towards this count.

7. Every entity must support all 4 CRUD operations, i.e., create/add, read/get, update/edit and delete.
   - You must handle any "side effects" of these operations on an entity to other entities related to the entity.
    * E.g., Recall how you needed to update loads when deleting a boat.
   - Update for an entity should support both PUT and PATCH.

8. Every CRUD operation for an entity related to a user must be protected and require a valid JWT corresponding to the relevant user.

9. You must provide an endpoint to create a relationship and another to remove a relationship between the two non-user entities. It is your design choice to make these endpoints protected or unprotected.
   - E.g., In Assignment 4, you had provided an endpoint to put a load on a boat, and another endpoint to remove a load from a boat.

10. If an entity has a relationship with other entities, then this info must be displayed in the representation of the entity
    - E.g., if a load is on a boat, then
    * The representation of the boat must show the relationship with this load
    * The representation of this load must show the relationship with this boat

11. There is no requirement to provide dedicated endpoints to view just the relationship
- E.g., Assignment 4 required an endpoint GET /boats/:boat_id/loads. Such an endpoint is not required in this project.

12. For endpoints that require a request body, you only need to support JSON representations in the request body.
- Requests to some endpoints, e.g., GET don't have a body. This point doesn't apply to such endpoints.
 
13. Any response bodies should be in JSON, including responses that contain an error message.
- Responses from some endpoints, e.g., DELETE, don't have a body. This point doesn't apply to such endpoints.
- In some cases error message may get generated by the web server and your code may not even get invoked. This point about JSON response body doesn't apply in such cases.

14. Any request to an endpoint that will send back a response with a body must allow 'application/json' in the Accept header. If a request doesn't have such a header, it should be rejected.

## User Details
1. You must support the ability for users of the application to create user accounts. There is no requirement to edit or delete users.

2. You may choose from the following methods of handling user accounts
   * You can handle all account creation and authentication yourself.
   * You can use a 3rd party authentication service (e.g., Auth0).

3. You must provide a URL where a user can provide a username/email address, and a password to login or to create a user account. If you are using Auth0, this can be a URL in your app that redirects to Auth0.

4. You must have a User entity in your database which stores at least the unique user ID of each user of your application
   * The first time someone logs in and generates a JWT in your app they must be added as a user in the User entity of your database.

5. Requests for the protected resources must use a JWT for authentication. So you must show the JWT to the user after the login. You must also show the user's unique ID after login.

6. The choice of what to use as the user's unique ID is up to you
   * You can use the value of "sub" from the JWT as a user's unique ID. But this is not required.

7. You must provide an unprotected endpoint GET /users that returns all the users currently registered in the app, even if they don't currently have any relationship with a non-user entity. The response does not need to be paginated
   * Minimally this endpoint should display the unique ID for a user. Beyond that it is your choice what else is displayed.

8. There is no requirement for an integration at the UI level between the login page and the REST API endpoints
   * The graders will login using the app's login/create user account URL.
   * Copy the JWT displayed and manually paste it in the Postman environment files to run the tests.

## Status Code
* 200
* 201
* 204
* 401
* 403
* 405
* 406

## POSTMAN
In the Postman folder, there are json files for Postman's environment variables and Postman collections.
  - Distribution location: https://cs493-assignment3-403322.uw.r.appspot.com
   * ohjeo_project.postman_collection.json
   * ohjeo_project.postman_environment.json
   * The ohjeo_project.pdf file indicates responses to requests that can be expected.



