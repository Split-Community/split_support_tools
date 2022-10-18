import Vue from 'vue';
import Vuex from 'vuex';

import { MAKE_URL } from '@/js/utils';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    apiKey: '',
    workspaces: [],
    currentWorkspace: null,
    environments: [],
    splits: [],
  },
  mutations: {
    SET_WORKSPACES(state, workspaces) {
      state.workspaces = workspaces;
    },
    SET_WORKSPACE(state, workspace) {
      state.currentWorkspace = workspace;
    },
    SET_ENVIRONMENTS(state, environments) {
      state.environments = environments;
    },
    SET_SPLITS(state, splits) {
      state.splits = splits;
    },
  },
  actions: {
    async GET_WORKSPACES(context) {
      const limit = 10;
      let offset = 0;
      let currentPage = 0;
      let maxPage = Infinity;
      const workspaces = [];

      while (currentPage <= maxPage) {
        const response = await fetch(`${MAKE_URL('v2/workspaces')}?limit=${limit}&offset=${offset}`, {
          method: 'GET', 
          headers: {
            Accept: 'application/json',
            Authorization: `Bearer ${context.state.apiKey}`
          }
        });
        if (response.ok) {
          const response_json = await response.json();
          workspaces.push(...response_json['objects']);
          maxPage = Math.max(0, Math.ceil(response_json["totalCount"] / limit) - 1);
          currentPage += 1;
          offset = offset + limit;
        } else {
          const res = await response.text();
          console.error(res);
        }
      }
      context.commit('SET_WORKSPACES', workspaces);
      Vue.$toast.success('Got workspaces list!');
    },
    async GET_ENVIRONMENTS(context) {
      const response = await fetch(`${MAKE_URL(`v2/environments/ws/${context.state.currentWorkspace}`)}`, {
        method: 'GET', 
        headers: {
          Accept: 'application/json',
          Authorization: `Bearer ${context.state.apiKey}`
        }
      });
      if (response.ok) {
        const response_json = await response.json();
        context.commit('SET_ENVIRONMENTS', response_json);
        Vue.$toast.success('Got environments list!');
      } else {
        const res = await response.text();
        console.error(res);
      }
    },
    async GET_SPLITS(context) {
      const limit = 10;
      let offset = 0;
      let currentPage = 0;
      let maxPage = Infinity;
      const splits = [];

      while (currentPage <= maxPage) {
        const response = await fetch(`${MAKE_URL(`v2/splits/ws/${context.state.currentWorkspace}`)}?limit=${limit}&offset=${offset}`, {
          method: 'GET', 
          headers: {
            Accept: 'application/json',
            Authorization: `Bearer ${context.state.apiKey}`
          }
        });
        if (response.ok) {
          const response_json = await response.json();
          splits.push(...response_json['objects']);
          maxPage = Math.max(0, Math.ceil(response_json["totalCount"] / limit) - 1);
          currentPage += 1;
          offset = offset + limit;
        } else {
          const res = await response.text();
          console.error(res);
        }
      }
      context.commit('SET_SPLITS', splits);
      Vue.$toast.success('Got splits list!');
    },
  },
  getters: {
    API_KEY(state) {
      return state.apiKey;
    },
    WORKSPACES(state) {
      return state.workspaces;
    },
    SPLITS(state) {
      return state.splits;
    },
    ENVIRONMENTS(state) {
      return state.environments;
    },
    CURRENT_WORKSPACE(state) {
      return state.currentWorkspace;
    },
  }
});
