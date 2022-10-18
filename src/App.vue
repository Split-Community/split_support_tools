<template>
  <div id="app">
    <b-navbar type="dark" variant="info">
      <b-navbar-brand>Split Definition Copier</b-navbar-brand>
    </b-navbar>

    <b-container id="main-container" fluid>
      <b-row>
        <b-col cols="4">
          <APIConfig />
        </b-col>
        <b-col cols="8">
          <CopierComponent />
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import APIConfig from './components/APIConfig.vue';
import CopierComponent from './components/CopierComponent.vue';

export default {
  name: 'App',
  components: {
    APIConfig,
    CopierComponent,
  },
};
</script>

<style scoped>
#main-container {
  margin-left: 0;
  margin-right: 0;
}
</style>
