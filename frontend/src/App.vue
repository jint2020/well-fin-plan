<template>
  <el-container class="app-shell">
    <el-aside width="220px" class="sidebar">
      <h1>资金管理</h1>
      <el-menu router :default-active="$route.path">
        <el-menu-item index="/">月度仪表盘</el-menu-item>
        <el-menu-item index="/transactions">流水记录</el-menu-item>
        <el-menu-item index="/settings">参数设置</el-menu-item>
        <el-menu-item index="/emergency-fund">应急金</el-menu-item>
        <el-menu-item index="/debts">债务管理</el-menu-item>
        <el-menu-item index="/assets">资产配置</el-menu-item>
        <el-menu-item index="/goals">目标计划</el-menu-item>
      </el-menu>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>
