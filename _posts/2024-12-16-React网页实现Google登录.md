---
title: React网页实现Google登录
date: 2024-12-14 10:00:00 +0800
categories: [React]
tags: [编程] # TAG names should always be lowercase
---

## 省流：

package.json 和 auth.js 里面改了全局启动就可以，而且即使说登录按钮被弃用了，但 2024 年 12 月的时候，全局启动服务器之后，也还能用。换了新库的登录按钮，就是 res 传回的信息格式变了。之后会怎样我也不知道。

至于为什么在 auth.js 里面设置就可以覆盖整个 Node 服务器：

1.**全局设置的影响**：

- require("https").globalAgent = proxyAgent  这行代码会影响整个  Node.js 进程
- 所有的  HTTPS 请求都会使用这个代理设置
- 不需要在每个文件中都设置

**2.模块加载顺序**：

- server.js 加载 auth.js
- auth.js 中的代理设置在模块加载时就生效
- 之后的所有网络请求都会使用这个设置

**3.作用域**：

- 代理设置是进程级别的
- 不需要在每个需要网络请求的地方都设置
- 一次设置，全局生效

所以，虽然我们只在  auth.js  中设置了代理，但它会影响整个  Node.js  服务器进程的所有网络请求。这就是为什么只需要在一个地方设置就够了。不过，如果你想让代码更清晰，也可以把代理设置移到 server.js：

require("https").globalAgent = new HttpsProxyAgent(process.env.HTTPS_PROXY);

const app = express();

这样可能更符合直觉，因为它清楚地表明这是一个全局设置。但实际上，放在 auth.js 里也完全没问题，因为：

- 只有 auth.js 需要访问被墙的服务
- 代理设置会在模块加载时就生效
- 保持相关代码的集中管理

## 1,谷歌登录按钮

原来的库显示已弃用：

Your client application uses libraries for user authentication or authorization that are deprecated. See the [Migration Guide](https://developers.google.com/identity/gsi/web/guides/gis-migration) for more information.

新的库：@react-oauth/google

```css
npm i @react-oauth/google
```

index.js:

注意，这里的 clientid 也要变成自己的，他公用的不能用。

```jsx
import React from "react";
import ReactDOM from "react-dom";
import App from "./components/App.js";

import { GoogleOAuthProvider } from "@react-oauth/google";

ReactDOM.render(
  <GoogleOAuthProvider clientId="5976">
    <React.StrictMode>
      <App />
    </React.StrictMode>
  </GoogleOAuthProvider>,
  document.getElementById("root")
);

// allows for live updating
module.hot.accept();
```

新库只有 GoogleLogin 作为按钮，没有 GoogleLogout 按钮。但是登录、登出都可以用相应函数去绑定一个 button，登录的是 useGoogleLogin，登出的是 googleLogout。

这里要注意，GoogleLogin 作为按钮和自定义按钮用 useGoogleLogin 函数，accounts.google 返回的 object 的格式不一样。

同时如果自定义的按钮，调用的 useGoogleLogin 函数，也有在网页上设置了一个用户图片、用户名的 state，移植过来不用 axios，

自定义按钮查阅这篇博客：https://muhammedsahad.medium.com/react-js-a-step-by-step-guide-to-google-authentication-926d0d85edbd

```jsx
  const [profile, setProfile] = useState([]);
  const [user, setUser] = useState([]);

useEffect(() => {
    if (user) {
      get("https://www.googleapis.com/oauth2/v1/userinfo", {
        access_token: user.access_token,
        headers: {
          Authorization: `Bearer ${user.access_token}`,
          Accept: "application/json",
        },
      })
        .then((res) => {
          setProfile(res);
        })
        .catch((err) => console.log(err));
    }
  }, [user]);

//登录函数
const login = useGoogleLogin({
    onSuccess: (codeResponse) => {
      console.log(codeResponse);
      setLoggedIn(true);
      setUser(codeResponse);
    onError: (error) => console.log("Login Failed:", error),
  });

  //按钮部分
  loggedIn ? (
            <div className="NavBar-link NavBar-login">
              <img src={profile.picture} alt="user image" />
              <h3>User Logged in</h3>
              <p>Name: {profile.name}</p>
              <p>Email Address: {profile.email}</p>
              <br />
              <br />
              <button onClick={logOut}>Log out</button>
            </div>
          ) : (
            <GoogleLogin
              onSuccess={handleLogin}
              onFailure={(err) => console.log(err)}
              className="NavBar-link NavBar-login"
            />
          )
        }
```

## 这里主要延续 MIT 的课继续。

NavBar.js:按钮更新库之后，传回来的 response 也会变结构,所以要改成 res.credential 传给后端。

NavBar.js:

```jsx
import React, { useState, useEffect } from "react";
import { Link } from "@reach/router";

import { GoogleLogin } from "@react-oauth/google";
import { useGoogleLogin } from "@react-oauth/google";
import { get, post } from "../../utilities";
import "./NavBar.css";
import { googleLogout } from "@react-oauth/google";

// This identifies your web application to Google's authentication service
const CLIENT_ID = "597664tent.com";

/**
 * The navigation bar at the top of all pages. Takes no props.
 */
const NavBar = (props) => {
  const [loggedIn, setLoggedIn] = useState(false);

  // TODO: call whoami to set loggedin state

  const logOut = () => {
    googleLogout();
    post("/api/logout");
    setLoggedIn(false);
  };

  const handleLogin = (res) => {
    // 'res' contains the response from Google's authentication servers
    console.log(res);
    setLoggedIn(true);
    const userToken = res.credential;
    post("/api/login", { token: userToken }).then((user) => {
      // the server knows we're logged in now
      console.log(user);
    });
  };

  const handleLogout = () => {
    googleLogout();
    console.log("Logged out successfully!");
    setLoggedIn(false);
    post("/api/logout");
  };

  return (
    <nav className="NavBar-container">
      <div className="NavBar-title u-inlineBlock">Catbook</div>
      <div className="NavBar-linkContainer u-inlineBlock">
        <Link to="/" className="NavBar-link">
          Home
        </Link>
        <Link to="/profile/" className="NavBar-link">
          Profile
        </Link>
        {loggedIn ? (
          <div className="NavBar-link NavBar-login">
            <button onClick={handleLogout}>Log out</button>
          </div>
        ) : (
          <GoogleLogin
            onSuccess={handleLogin}
            onFailure={(err) => console.log(err)}
            className="NavBar-link NavBar-login"
          />
        )}
      </div>
    </nav>
  );
};

export default NavBar;
```

## 让 Node 服务器代理启动

访问 account.google 时可以拿到 response，但是后端访问 googleapis 却访问不到，具体原因就是后端服务器没有通过代理。

首先确保 Clash 正确配置：

- 系统代理已开启（System Proxy）
- 允许局域网连接（Allow LAN）
- 记住代理端口（默认  7890）
- 最好切换到"全局模式"进行测试

**安装必要的  npm  包**

npm install https-proxy-agent cross-env --save-dev

**修改  package.json**

```css
{
"scripts": {
"start": "cross-env HTTPS_PROXY=http://127.0.0.1:7890 HTTP_PROXY=http://127.0.0.1:7890 node server.js"
}
}
```

**在服务器代码中设置代理**

auth.js:

```jsx
const User = require("./models/user");

const { HttpsProxyAgent } = require("https-proxy-agent");
const { OAuth2Client } = require("google-auth-library");
// create a new OAuth client used to verify google sign-in
const CLIENT_ID = "59766tent.com";
// 确保在最开始就设置环境变量
process.env.HTTPS_PROXY = process.env.HTTPS_PROXY || "http://127.0.0.1:7890";
process.env.HTTP_PROXY = process.env.HTTP_PROXY || "http://127.0.0.1:7890";

console.log("HTTPS_PROXY:", process.env.HTTPS_PROXY);
console.log("HTTP_PROXY:", process.env.HTTP_PROXY);

const proxyAgent = new HttpsProxyAgent(process.env.HTTPS_PROXY);

// 设置全局代理
require("https").globalAgent = proxyAgent;
require("http").globalAgent = proxyAgent;

// 替换成你的代理端口

const client = new OAuth2Client({
  clientId: CLIENT_ID,
  httpAgent: proxyAgent,
  httpsAgent: proxyAgent,
});
// accepts a login token from the frontend, and verifies that it's legit
function verify(token) {
  console.log("Starting token verification...");
  console.log("Using proxy:", process.env.HTTPS_PROXY);
  return client
    .verifyIdToken({
      idToken: token,
      audience: CLIENT_ID,
      requestOptions: {
        agent: proxyAgent,
        timeout: 10000, // 10 秒超时
      },
    })
    .then((ticket) => ticket.getPayload());
}

// gets user from DB, or makes a new account if it doesn't exist yet
function getOrCreateUser(user) {
  // the "sub" field means "subject", which is a unique identifier for each user
  return User.findOne({ googleid: user.sub }).then((existingUser) => {
    if (existingUser) return existingUser;

    const newUser = new User({
      name: user.name,
      googleid: user.sub,
    });

    return newUser.save();
  });
}

function login(req, res) {
  console.log("Received login request");
  verify(req.body.token)
    .then((user) => {
      console.log("Token verified successfully");
      return getOrCreateUser(user);
    })
    .then((user) => {
      console.log(`Logged in as ${user.name}`);

      // persist user in the session
      req.session.user = user;
      res.send(user);
    })
    .catch((err) => {
      console.log(`Failed to log in: ${err}`);
      res.status(401).send({ err });
    });
}

function logout(req, res) {
  if (req.user) console.log(`${req.user.name} logged out`);
  req.session.user = null;
  res.send({});
}

function populateCurrentUser(req, res, next) {
  // simply populate "req.user" for convenience
  req.user = req.session.user;
  next();
}

function ensureLoggedIn(req, res, next) {
  if (!req.user) {
    return res.status(401).send({ err: "not logged in" });
  }

  next();
}

module.exports = {
  login,
  logout,
  populateCurrentUser,
  ensureLoggedIn,
};
```
