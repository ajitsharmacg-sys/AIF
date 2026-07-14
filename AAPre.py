async submit_predisclosure() {

    await postData(

        api_endpoints.predisclosure_status,

        {

            predisclosure:
                this.selected_predisclosure
                    .predisclosure_id,

            status: "IN_PROGRESS",

            comment: "Submitted",

        }

    )
    .then(response => {

        if (response.ok) {

            this.show_notification(
                "PreDisclosure submitted successfully."
            );

            this.update_triggered = true;

            return;
        }

        return Promise.reject(response);

    })
    .catch(error => {

        this.display_error(error);

    });

}



<div class="btn-group">

    <button
        v-if="['DRAFT','REJECTED'].includes(actionProps?.predisclosure_status)"
        class="btn btn-sm btn-primary"
        @click="navigate('predisclosure_app','edit')">

        Edit

    </button>

    <button
        v-if="actionProps?.predisclosure_status == 'DRAFT'"
        class="btn btn-sm btn-success"
        @click="submit_predisclosure()">

        Submit

    </button>

</div>
