# Dosh

## Introduction

這是一個平臺，各個使用者可以 ssh 上來這個特製工作站，連上來之後會進入一個功能受限的 Shell，在上面可以創建、銷毀 Containers，而真正的操作便是讓你進入 Containers，以 Container 中的 root 權限去做，你可以得到一個絕對自由的環境。

由於容器化最著名的一套工具叫做 Docker，因此得名 Docker Shell，簡稱 Dosh。原是交大資工系計中推出的服務，但由於開發者畢業，無人維護，僅上線不到一年就下架。

本人對 Kubernetes 技術一直頗感興趣，於是便希望能重啓這個專案，來磨練本人的 Kubernetes 能力，而本系列教學也會根據本人的開發進展推進；如果中途使用了其它技術，值得一提的也會整理出來分享給大家。

---

It's the platform allow people to access it via ssh. After connecting to the machine, you would enter a limited shell, named dosh, you can create and destroy containers on that. Hence, the real thing you should do is do everything you want to do inside the container with root previlege (Sure, not including attacking or hacking).

Because of the most famous container tools Docker, it got its name, Docker Shell(Dosh). It was the service published by CSCC, NYCU in Taiwan. Unfortunately, it is no longer maintained or operated.

However, because of my strong interest in Kubernetes tech, and also feel interesting in this project, I decided to relaunch this project and start to learn Kubernetes during the development progress of this project. And I woule like to share my experiences in Kubernetes and the information of other interesting tools if I use in this project in the future.

## Demo

![](https://i.imgur.com/ciJGnRE.png)
![](https://i.imgur.com/Y4zfSV7.png)

## Also See

- [Kubernetes Tutorial](https://sandb0x.tw/index)
- [Dosh Developer Diary](https://sandb0x.tw/b/dosh_%E9%96%8B%E7%99%BC%E6%97%A5%E8%AA%8C.md)

