<template>
    <div>
        <b-form @submit="onSubmit" @reset="onReset">
            <b-form-group id="input-group-1" label="Admin API key:" label-for="input-1">
                <b-form-input id="input-1" v-model="form.apiKey" placeholder="Enter admin API key" required></b-form-input>
            </b-form-group>

            <b-button class="mr-1" type="submit" variant="primary">Connect</b-button>
            <b-button class="mr-1" type="reset" variant="danger">Reset</b-button>
        </b-form>
    </div>
</template>

<script>
export default {
  name: 'APIConfig',
  data() {
    return {
      form: {
        apiKey: '',
      },
    };
  },
  methods: {
    onSubmit(event) {
      event.preventDefault();
      this.$store.state.apiKey = this.form.apiKey;
    },
    onReset(event) {
      event.preventDefault();
      // Reset our form values
      this.form.apiKey = '';
      // Trick to reset/clear native browser form validation state
      this.show = false;
      this.$nextTick(() => {
        this.show = true;
      });
    },
  },
};
</script>
