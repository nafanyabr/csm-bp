<template>
  <div>
    <main class="main">
      <div class="container-fluid" id="ZkSearch">
        <div class="row">
          <div class="col-sm-9"></div>
          <div class="col-sm-3 text-right">
            <select v-model="userid" disabled>
              <option
                v-for="user in users"
                v-bind:value="user.id"
                v-bind:key="user.id"
              >{{ user.name }}</option>
            </select>
          </div>
        </div>
        <div class="row">
          <div class="col-sm-4">
            <div class="card">
              <div class="card-header">
                <strong>1. Поиск ЗК</strong>
              </div>
              <div class="card-body">
                <form class="form-horizontal" v-on:submit.prevent="getZk">
                  <div class="form-group row">
                    <div class="col-md-12">
                      <p>По штрих-коду из правого нижнего угла или по номеру и году ЗК</p>
                      <div class="input-group">
                        <div class="input-group-prepend">
                          <select class="form-control" v-model="zk_prefix">
                            <option
                              v-for="prefix in prefixes"
                              v-bind:value="prefix.id"
                              v-bind:key="prefix.id"
                            >{{prefix.text}}</option>
                          </select>
                        </div>
                        <input
                          v-model="zk_nomer"
                          class="form-control"
                          id="zk_nomer"
                          type="text"
                          name="zk_nomer"
                          placeholder="Номер ЗК или штрих-код"
                        />
                        <div class="input-group-append">
                          <select class="form-control" v-model="zk_year">
                            <option
                              v-for="year in years"
                              v-bind:value="year.id"
                              v-bind:key="year.id"
                            >{{year.id}}</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="row align-items-center">
                    <div class="col-6 col-sm-4 col-md-2 col-xl mb-3 mb-xl-0">
                      <button class="btn btn-danger" type="button" v-on:click="clearSearchFields">
                        <i class="fa fa-ban"></i> Очистить
                      </button>
                    </div>
                    <div class="col-6 col-sm-4 col-md-2 col-xl mb-3 mb-xl-0">
                      <button class="btn btn-primary" type="button" v-on:click="getZk">
                        <i class="fa fa-search"></i> Начать поиск
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>
          <div class="col-sm-8">
            <div class="card">
              <div class="card-header">
                <strong>2. Переместить выбранные типы СИ ({{selected.length}})</strong>
              </div>
              <div class="card-body">
                <form class="form-horizontal">
                  <div class="form-group row">
                    <label class="col-md-3 col-form-label" for="upd-comment">Комментарий/кол-во</label>
                    <div class="col-md-9">
                      <input
                        v-model="comment"
                        class="form-control"
                        id="upd-comment"
                        type="text"
                        name="upd-comment"
                        placeholder="Введите кол-во СИ или комментарий"
                      />
                    </div>
                  </div>
                  <div class="form-group row">
                    <label class="col-md-3 col-form-label" for="upd-location">Полка/место</label>
                    <div class="col-md-9">
                      <input
                        v-model="location"
                        class="form-control"
                        id="upd-location"
                        type="text"
                        name="upd-location"
                        placeholder="Укажите место/полку"
                      />
                      <span class="help-block">Можно отсканировать штрих-код полки</span>
                    </div>
                  </div>
                  <div class="row align-items-center">
                    <div class="col-6 col-sm-4 col-md-2 col-xl mb-3 mb-xl-0">
                      <button
                        class="btn btn-square btn-block btn-light"
                        type="button"
                        v-on:click="updateSi(1)"
                      >Бюро приёма</button>
                    </div>
                    <div class="col-6 col-sm-4 col-md-2 col-xl mb-3 mb-xl-0">
                      <button
                        class="btn btn-square btn-block btn-warning"
                        type="button"
                        v-on:click="updateSi(2)"
                      >Склад приёма</button>
                    </div>
                    <div class="col-6 col-sm-4 col-md-2 col-xl mb-3 mb-xl-0">
                      <button
                        class="btn btn-square btn-block btn-primary"
                        type="button"
                        v-on:click="updateSi(5)"
                      >Поверка</button>
                    </div>
                    <div class="col-6 col-sm-4 col-md-2 col-xl mb-3 mb-xl-0">
                      <button
                        class="btn btn-square btn-block btn-success"
                        type="button"
                        v-on:click="updateSi(4)"
                      >Склад выдачи</button>
                    </div>
                    <div class="col-6 col-sm-4 col-md-2 col-xl mb-3 mb-xl-0">
                      <button
                        class="btn btn-square btn-block btn-secondary"
                        type="button"
                        v-on:click="updateSi(3)"
                      >Выдано заказчику</button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-lg-12 mx-auto">
            <div class="card">
              <div class="card-header">
                <div class="row">
                  <div class="col-sm-9">
                    <strong
                      v-if="zk_info_num"
                    >{{ zk_info_num }} от {{ zk_info_date | rudate }}. {{ zk_info_customer }}. Всего строк: {{devices.length}}</strong>
                  </div>
                  <div class="col-sm-3 text-right">
                    <strong>Выбрано строк: {{selected.length}}</strong>
                  </div>
                </div>
              </div>
              <div class="card-body">
                <div v-if="zk_info_pay_date" class="alert alert-success" role="alert">
                  <span>
                    <strong>Оплата: {{zk_info_pay_date | rudate}}</strong>
                  </span>
                  <span v-if="zk_info_pay_procent">&nbsp;({{zk_info_pay_procent}}%)</span>
                </div>
                <table class="table table-responsive-sm table-striped table-sm">
                  <thead>
                    <tr class="text-center">
                      <th>
                        <input type="checkbox" v-model="selectAll" @click="selectAllDev" />
                      </th>
                      <th>Наименование СИ</th>
                      <th>Кол-во в ЗК/Назначено</th>
                      <th>Этап</th>
                      <th>Дата этапа</th>
                      <th>Коммент/кол-во</th>
                      <th>Место</th>
                      <th>Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(device) in devices"
                      v-bind:key="device.op_id"
                      v-bind:title="device.device_name"
                    >
                      <td class="text-center">
                        <input
                          type="checkbox"
                          :value="device.op_id"
                          v-model="selected"
                          @click="selectDev(device.op_id)"
                        />
                      </td>
                      <td
                        v-bind:id="device.op_id"
                        class="text-left"
                      >{{device.device_name}}&nbsp;{{device.device_mark}}</td>
                      <td class="text-center">{{device.qty}}/{{device.nazn}}</td>
                      <td class="text-center">
                        <span
                          v-bind:class="{'badge':true, 'badge-success': device.destination_id == 4, 'badge-warning': device.destination_id == 2, 'badge-secondary': device.destination_id == 3, 'badge-primary': device.destination_id == 5}"
                        >{{device.destination_name}}</span>
                      </td>
                      <td class="text-center">{{device.accept_date | rudate}}</td>
                      <td class="text-center">{{device.COMMENT}}</td>
                      <td class="text-center">{{device.LOCATION}}</td>
                      <td class="text-center">
                        <span v-show="device.work_done" title="Работы завершены">
                          <i class="fa fa-check-circle"></i>
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="error_text" class="alert alert-danger" role="alert">
                  <strong>{{ error_text }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
    <footer class="app-footer">
      <div>
        ФБУ "Брянский ЦСМ"
        <span>© 2019 Александр Куликов</span>
      </div>
      <div class="ml-auto">
        <span>Учёт движения СИ. Версия 0.5 - 20190912</span>
      </div>
    </footer>
  </div>
</template>

<script>
import axios from "axios";

export default {
  props: ["userid"],
  data() {
    return {
      error_text: "",
      devices: [],
      selected: [],
      selectAll: false,
      zk_nomer: "",
      zk_prefix: "bp",
      zk_year: "2019",
      comment: "",
      location: "",
      zk_info_num: "",
      zk_info_customer: "",
      zk_info_date: "",
      zk_info_pay_date: "",
      zk_info_pay_procent: "",
      users: [
        { id: "303", name: "Алещенко Л.В." },
        { id: "305", name: "Власенкова Е.А." },
        { id: "261", name: "Иванина М.Г." },
        { id: "392", name: "Карпекина И.М." },
        { id: "432", name: "Лалазарова К.П." },
        { id: "327", name: "Салтыкова М.Ю." }
      ],
      years: [{ id: 2019 }, { id: 2018 }, { id: 2017 }],
      prefixes: [
        { id: "bp", text: "БП-" },
        { id: "gz", text: "ГЗ-" },
        { id: "d", text: "Д-" },
        { id: "kp", text: "КП-" },
        { id: "no", text: "нет" }
      ]
    };
  },
  methods: {
    clearSearchFields() {
      (this.zk_nomer = ""),
        (this.zk_prefix = "bp"),
        (this.zk_year = "2019"),
        (this.devices = []),
        (this.selected = []),
        (this.selectAll = false),
        (this.zk_info_num = ""),
        (this.zk_info_customer = ""),
        (this.comment = ""),
        (this.location = ""),
        (this.error_text = ""),
        (this.zk_info_pay_date = ""),
        (this.zk_info_pay_procent = ""),
        (this.zk_info_date = "");
    },
    getZk() {
      if (this.zk_nomer) {
        axios
          .get("/api/v1/orders", {
            params: {
              zk_prefix: this.zk_prefix,
              zk_nomer: this.zk_nomer,
              zk_year: this.zk_year
            }
          })
          .then(res => {
            if (res.data["status"] == "error") {
              this.comment = "";
              this.location = "";
              this.devices = "";
              this.zk_info_num = "";
              this.zk_info_customer = "";
              this.zk_info_date = "";
              this.zk_info_pay_date = "";
              this.zk_info_pay_procent = "";
              this.selected = [];
              this.selectAll = false;
              this.error_text = res.data["error_text"];
            } else {
              this.comment = "";
              this.location = "";
              this.devices = res.data["devices"];
              this.zk_info_num = res.data["local_id"];
              this.zk_info_customer = res.data["CUSTOMER_NAME"];
              this.zk_info_date = res.data["date"];
              this.zk_info_pay_date = res.data["payment_date"];
              this.zk_info_pay_procent = res.data["payment_num"];
              this.selectAll = false;
              this.selectAllDev();
              this.selectAll = true;
            }
            console.log(res);
          })
          .catch(err => {
            console.log(err);
          });
      }
    },
    updateSi(destination_id) {
      axios
        .post("/api/v1/transport", {
          destination_id: destination_id,
          employee_id: this.userid,
          dep_id: "52010030",
          order_pos_ids: this.selected,
          comment: this.comment,
          location: this.location
        })
        .then(res => {
          this.getZk();
          console.log(res);
        })
        .catch(err => {
          console.log(err);
        });
    },
    selectDev(device_id) {
      if (this.selected.includes(device_id)) {
        this.selected.splice(this.selected.findIndex(v => v === device_id), 1);
      } else {
        this.selected.push(device_id);
      }
    },
    selectAllDev() {
      this.selected = [];
      if (!this.selectAll) {
        for (let i in this.devices) {
          this.selected.push(this.devices[i].op_id);
        }
      }
    }
  }
};
</script>

