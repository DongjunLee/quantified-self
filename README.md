<p align="center">
  <img src="images/qs.gif">
</p>
<p align="center">
  <img src="images/kino.png" style="inline">
</p>

<h1 align="center"> kino-bot </h1>
<h3 align="center">
  <sup><strong>
    A.I Personal Assistant Based on Slack Bot
  </strong></sup>
</h3>

<p align="center">
  <a href="https://github.com/DongjunLee/stalker-bot">
    <img src="https://img.shields.io/badge/Quantified%20Self-Slack%20Bot-brightgreen.svg" alt="Project Introduction">
  </a>
  <a href="https://travis-ci.org/badges/shields">
    <img src="https://travis-ci.org/DongjunLee/stalker-bot.svg?branch=master" alt="build status">
  </a>
  <a href="https://codecov.io/gh/DongjunLee/stalker-bot">
    <img src="https://codecov.io/gh/DongjunLee/stalker-bot/branch/master/graph/badge.svg" alt="Codecov" />
  </a>
</p>

## Introduce
 
 Kino는 Slack Bot으로 기본으로 개발된 Personal Assistant A.I 입니다. 일반적으로 사용되는 분야가 아닌, 저에게 필요한 부분들을 개발하여 저 자신의 삶의 질을 높이기 위한 개인 프로젝트 (BeHappy 프로젝트) 입니다. 다양한 Tracking Tool들 (cf. [RescueTime](https://www.rescuetime.com/), [Toggl](https://toggl.com/), ) 및 다양한 서드 파티(cf. [Github](https://github.com/) 와 연동하여 자신에 대해서 더 자세히 파악하고 그에 맞는 반응을 하는 봇을 개발합니다. 
 
 물론 머신러닝과 딥러닝도 사용하여 단순한 기능 연동을 넘어서 똑똑한 비서로서 성장시킬 것 입니다.

## Prerequisites

- [slacker](https://github.com/os/slacker)
- [PyGithub](https://github.com/PyGithub/PyGithub)
- [schedule](https://github.com/dbader/schedule)

## Features

- Alarm Manager (Scheduler)
	- 정해진 시간동안 일정 주기로 메시지를 전송
	- ex) 07:00~08:00, 20분 주기로 '굿모닝! 일어나세요!' 메시지를 전송

## Usages

- Alarm Manager (Scheduler)
	- 알람간격 보기
	- 알람간격 등록 <시간간격> + <설명>
	- 알람간격 변경 <인덱스> + <시간간격> + <설명>
	- 알람간격 삭제 <인덱스>
	- 알람 보기
	- 알람 등록  <메시지 받을 텍스트> + <반복주기> + <알림간격 인덱스>
	- 알람 변경  <인덱스> + <메시지 받을 텍스트> + <반복주기> + <알림간격 인덱스>
	- 알람 삭제  <인덱스>
	- 알람 시작/중지
- Example.
<p align="center">
	<img src="images/between_create.png" width=275 style="inline">
	<img src="images/between_read.png" width=275 style="inline">
	<img src="images/alarm_create.png" width=250 style="inline">
	<img src="images/alarm_read.png" width=300 style="inline">
	<img src="images/alarm_start_stop.png" width=200 style="inline">
</P>


