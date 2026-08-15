# API Credential Setup Guide

The system requires Instagram and TikTok API credentials to function properly. Since no existing credentials were found in the system, you'll need to obtain them from the respective platforms.

## Instagram API Credentials

### Required Credentials:
- **Instagram Graph API Access Token**
- **Instagram App ID** (Client ID)
- **Instagram App Secret** (Client Secret)

### How to Obtain:

1. **Create Instagram Developer Account**
   - Go to https://developers.facebook.com/
   - Create a developer account
   - Verify your identity

2. **Create an App**
   - Go to https://developers.facebook.com/apps/
   - Click "Create App"
   - Select "Consumer" app type
   - Fill in app details

3. **Add Instagram Product**
   - In your app dashboard, add "Instagram Graph API"
   - Configure Instagram Basic Display or Instagram Graph API

4. **Generate Access Token**
   - Go to Instagram Basic Display settings
   - Add a tester (your Instagram account)
   - Generate access token
   - Copy the access token

### Required Environment Variables:
```bash
INSTAGRAM_API_KEY=your_access_token
INSTAGRAM_ACCESS_TOKEN=your_access_token
INSTAGRAM_CLIENT_ID=your_app_id
INSTAGRAM_CLIENT_SECRET=your_app_secret
```

## TikTok API Credentials

### Required Credentials:
- **TikTok API Key** (Access Token)
- **TikTok Client ID**
- **TikTok Client Secret**

### How to Obtain:

1. **Create TikTok Developer Account**
   - Go to https://developers.tiktok.com/
   - Sign up for a developer account
   - Verify your identity

2. **Create an App**
   - Go to https://developers.tiktok.com/apps
   - Click "Create App"
   - Select app type (e.g., "Creator" or "Business")
   - Fill in app details

3. **Generate API Key**
   - In your app dashboard, go to "Keys"
   - Generate API key/secret pair
   - Copy the credentials

### Required Environment Variables:
```bash
TIKTOK_API_KEY=your_access_token
TIKTOK_CLIENT_ID=your_client_id
TIKTOK_CLIENT_SECRET=your_client_secret
```

## Quick Setup with CLI

Once you have the credentials, use the CLI to set them:

```bash
# Set Instagram credentials
instagran-api capture-keys --manual INSTAGRAM_API_KEY your_token_here
instagran-api capture-keys --manual INSTAGRAM_CLIENT_ID your_client_id
instagran-api capture-keys --manual INSTAGRAM_CLIENT_SECRET your_secret

# Set TikTok credentials
instagran-api capture-keys --manual TIKTOK_API_KEY your_token_here
instagran-api capture-keys --manual TIKTOK_CLIENT_ID your_client_id
instagran-api capture-keys --manual TIKTOK_CLIENT_SECRET your_secret

# Verify captured keys
instagran-api capture-keys --list
```

## Alternative: Environment Variables

You can also set them directly in your environment:

```bash
export INSTAGRAM_API_KEY="your_token"
export INSTAGRAM_CLIENT_ID="your_client_id"
export INSTAGRAM_CLIENT_SECRET="your_secret"
export TIKTOK_API_KEY="your_token"
export TIKTOK_CLIENT_ID="your_client_id"
export TIKTOK_CLIENT_SECRET="your_secret"
```

## Testing Credentials

After setting credentials, test them:

```bash
# Test Instagram
instagran-api api-test --token test123 --username katiewynnz --platform instagram

# Test TikTok
instagran-api api-test --token test123 --username katiewynnz --platform tiktok
```

## Important Notes

- **Keep credentials secure**: Never commit API keys to git
- **Use test accounts**: Start with test accounts before production
- **Rate limits**: Be aware of API rate limits
- **Permissions**: Ensure your app has necessary permissions
- **Token expiration**: Access tokens may expire and need refresh

## Troubleshooting

If credentials don't work:
1. Verify the token hasn't expired
2. Check app permissions in developer portal
3. Ensure your account is added as tester
4. Verify the token has required scopes
5. Check API status pages for service issues

## Next Steps

1. Obtain credentials from Instagram and TikTok developer portals
2. Set credentials using the CLI commands above
3. Test with a known username
4. Run the full test suite with target users
