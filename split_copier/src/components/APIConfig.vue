<template>
    <b-container>
      <b-row v-if="API_KEY === ''" class="mt-3">
        <b-col>
          <b-form @submit="onSubmitKey">
            <b-form-group id="input-group-1" label="Admin API key:" label-for="input-1">
                <b-form-input id="input-1" v-model="form.apiKey" placeholder="Enter admin API key" required></b-form-input>
            </b-form-group>
            <b-button class="mr-1" type="submit" variant="primary">Connect</b-button>
          </b-form>
        </b-col>
      </b-row>
      <b-row class="mt-3" v-if="workspaceOptions.length > 1">
        <b-col>
          <b-form @submit="onSubmitWorkspace">
            <b-form-group id="input-group-1" label="Workspace:" label-for="input-1">
              <b-form-select id="input=1" :options="workspaceOptions" v-model="wsForm.workspace" />
            </b-form-group>
            <b-button class="mr-1" type="submit" variant="primary">Select Workspace</b-button>
          </b-form>
        </b-col>
      </b-row>
      <b-row v-if="API_KEY === ''" class="mt-3">
        <b-col>
          <b-button class="mr-1" variant="danger" @click="resetForms">Reset</b-button>
        </b-col>
      </b-row>
    </b-container>
</template>

<script>
import { mapMutations, mapActions, mapGetters } from 'vuex';
import { API_KEY } from '@/js/consts.js';

export default {
  name: 'APIConfig',
  data() {
    return {
      form: {
        apiKey: '',
      },
      wsForm: {
        workspace: null,
      },
      API_KEY: API_KEY,
    };
  },
  async mounted() {
    console.log('mounted');
    if (this.API_KEY !== '') {
      await this.GET_WORKSPACES();
    }
  },
  methods: {
    async onSubmitKey(event) {
      event.preventDefault();
      this.$store.state.apiKey = this.form.apiKey;
      await this.GET_WORKSPACES();
    },
    async onSubmitWorkspace(event){
      event.preventDefault();
      this.SET_WORKSPACE(this.wsForm.workspace);
      await this.GET_ENVIRONMENTS();
      await this.GET_SPLITS();
    },
    resetForms() {
      this.form.apiKey = null;
      this.wsForm.workspace = null;
      if (this.API_KEY !== '') {
        this.$store.state.apiKey = this.form.apiKey;
      }
      this.$store.state.currentWorkspace = this.wsForm.workspace;
      this.$store.state.workspaces = [];
      this.$store.state.environments = [];
      this.$store.state.splits = [];
    },
    ...mapActions(['GET_WORKSPACES', 'GET_ENVIRONMENTS', 'GET_SPLITS']),
    ...mapMutations(['SET_WORKSPACE']),
  },
  computed: {
    workspaceOptions() {
      return [
        { value: null, text: 'Select Workspace', disabled: true },
        ...this.WORKSPACES.map((ws) => ({ value: ws.id, text: ws.name }))
      ];
    },
    ...mapGetters(['WORKSPACES']),
  }
};
</script>
