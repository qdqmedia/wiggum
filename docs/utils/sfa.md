# SFA

Single factor authentication or SFA is a way of authenticating the user by one
check. Companies like twitter implement this by sending a link to a trusted medium
So the user can click on a link that will authenticate.

In Wiggum case, wiggum can generate a token that entering in the token will
generate  a JWT token and set to the user as if it entered the username & password.

This is useful as an alternative to the users that always forget the password. Wiggum
like reset token link, doesn't send the link by email. but you could easily send
it by email implementing a custom action.

the SFA links can be generate by [API], this will generate a url of the
`a/sfa/{ID}/{UUID}` type


[SFA]: utils/api/#special-actions
