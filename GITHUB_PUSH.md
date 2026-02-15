# Push to GitHub - Step by Step

## ✅ Already Done
- Git repository initialized
- All files committed locally
- .env excluded (API key safe)

## 📋 Next Steps

### 1. Create a New GitHub Repository

Go to: https://github.com/new

**Settings:**
- Repository name: `linkedin-referral-generator` (or your choice)
- Description: `AI-powered Streamlit app for generating casual LinkedIn referral messages`
- Visibility: **Public** or **Private** (your choice)
- ❌ **DO NOT** initialize with README, .gitignore, or license (we already have these)

Click **"Create repository"**

### 2. Push Your Code

After creating the repo, GitHub will show you commands. Use these:

```bash
git remote add origin https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
git branch -M main
git push -u origin main
```

**Replace** `<YOUR_USERNAME>` and `<REPO_NAME>` with your actual values.

### 3. Verify

Go to your repository URL and verify all files are there:
- ✅ app.py
- ✅ requirements.txt
- ✅ README.md
- ✅ .gitignore
- ✅ .env.example
- ❌ .env (should NOT be there - has your API key!)

## 🎉 Done!

Your project is now on GitHub and can be:
- Shared with others
- Cloned to other machines
- Deployed to Streamlit Cloud
- Contributed to by collaborators

---

## 🔒 Security Note

The `.env` file with your actual API key is **NOT** pushed to GitHub (it's in .gitignore). 
Others will need to:
1. Copy `.env.example` to `.env`
2. Add their own Google Gemini API key
