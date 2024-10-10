# Dosh (Docker Shell)

這是一個平臺，各個使用者可以 ssh 上來這個特製工作站，連上來之後會進入一個功能受限的 Shell，在上面可以創建、銷毀 Containers，而真正的操作便是讓你進入 Containers，以 Container 中的 root 權限去做，你可以得到一個絕對自由的環境。

由於容器化最著名的一套工具叫做 Docker，因此得名 Docker Shell，簡稱 Dosh。原是交大資工系計中推出的服務，但由於開發者畢業，無人維護，僅上線不到一年 就下架。

本人對 Kubernetes 技術一直頗感興趣，於是便希望能重啓這個專案，來磨練本人的 Kubernetes 能力，而本系列教學也會根據本人的開發進展推進；如果中途使用了其它技術，值得一提的也會整理出來分享給大家。

---

This is a platform that allow people connect to via ssh. When people get in the machine, they would enter a limited shell, named Dosh(Docker Shell), you could create and destroy containers on which.

The real thing you should do is to create a container and do anything you want to do inside the container(except using the network resource to attack other people).

Because of my keen interest in Kubernetes tech, I relaunched this project. This idea was from CSCC of National Chiao Tung University in Taiwan.
