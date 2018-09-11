$(function () {

    // Adiciona as mascaras para os inputs que possuirem
    // um valor para input-mask
    $(":input").inputmask();
    showTasks().init();
    
    var location = window.location.pathname;
    if (location in LOCATIONS) {
        LOCATIONS[location]();
    }

});


const LOCATIONS = {
    '/produtos/enviar': () => {
        var iniciar = produtosEnviarControl();
        iniciar.init();
    },
    '/categorias/importar': () => {
        var iniciar = categoriaImportarControl();
        iniciar.init();
    }
}


/**
 * Script para atualizar as tasks que sao executadas em segundo plano
 * no backend.
 */

var TaskModel = (function () {
    /**
     * Representa a model que vai conter todos os objetos das tarefas
     * em execução no backend
     */
    
     var Task = function (taskId, name, total, current, status) {
        this.id = getID();
        this.taskId = taskId;
        this.name = name;
        this.total = total;
        this.current = current;
        this.status = status;
    };

    var data = {
        tasks: []
    }

    var getID = function () {
        if (data.tasks.length > 0) {
            var lastTask = data.tasks.slice(-1)[0];
            return lastTask.id + 1;
        }
        return 1;
    }

    return {
        getTaskById: function (id) {
            data.tasks.forEach(function (task) {
                if (task.id === id) {
                    return task;
                }
            });
            return null;
        },

        createTask: function (taskId, name, total, current, status) {
            var task = new Task(taskId, name, total, current, status);
            data.tasks.push(task);
            return task;
        }
    }
});


var TaskUI = (function () {
    /**
     * Representa a parte visual das Tasks em execução. Ficara responsavel
     * por atualizar os dados na DOM para ficar visivel ao usuário.
     */

    var elements = {
        totalTasks: document.getElementById('total-tasks-qty'),
        button: document.getElementById('show-notify'),
        closeButton: document.querySelector('.close__'),
        tasks: document.getElementById('tasks'),
        tasksContent: document.getElementById('task_list')
    };

    var addTaskHTML = function (task) {
        var task = task;
        var currentPerc = parseInt((parseInt(task.current) * 100) / parseInt(task.total));
        
        var html = `
        <li id="task__${task.id}"> <p><b>Tarefa:</b>\r${task.name}\r<b>Status:</b>\r${task.current}/${task.total}</p>
            <div class="progress">
                <div class="progress-bar" role="progressbar" aria-valuenow="" aria-valuemin="0" aria-valuemax="100" style="width: ${currentPerc}%;">
                    ${currentPerc}%
                </div>
            </div>
        </li>
        `;

        elements.tasksContent.insertAdjacentHTML('beforeend', html);
    };

    var updateTaskHTML = function (task) {
        var taskElement = document.getElementById(`task__${task.id}`);
        var currentPerc = parseInt((parseInt(task.current) * 100) / parseInt(task.total));
        
        var html = `         
        <p><b>Tarefa:</b>\r${task.name}<b>\rStatus:</b>\r${task.current}/${task.total}</p>
        <div class="progress">
            <div class="progress-bar" role="progressbar" aria-valuenow="" aria-valuemin="0" aria-valuemax="100" style="width: ${currentPerc}%;">
                ${currentPerc}%
            </div>
        </div>
        `;

        taskElement.innerHTML = html;
    };

    var removeTaskHTML = function (task) {
        var taskElement = document.getElementById(`task__${task.id}`);
        taskElement.parentElement.removeChild(taskElement);
    }

    var clearTasks = function () {
        html = '<li><p>Não existem tarefas sendo processados.</p></li>'
        elements.tasksContent.innerHTML = html;
    }

    return {
        addTaskHTML: addTaskHTML,
        updateTaskHTML: updateTaskHTML,
        removeTaskHTML: removeTaskHTML,
        clearTasks: clearTasks
    }
});


var TaskControl = (function () {
    /**
     * Controller das Tasks. Tem como objetivo controlar todo o processo de
     * atualização das Tasks do servidor com a View na DOM.
     */
    
    var taskModel = TaskModel();
    var taskUI = TaskUI();
    var taskIDsList = [];
    var url = '/gettasks';

    // Filtra a lista de ids das tasks e retorna true se existe
    var filterTaskIDsList = function (taskID) {
        taskIDsList.forEach(function (registredTaskID) {
            if (taskID === registredTaskID) {
                return true;
            }
            return false;
        })
    };

    var update = function () {
        
    }

    var getTask = function (taskId) {
        return new Promise(function (resolve, reject) {
            $.ajax({
                url: `${url}/${taskId}`,
                success: function (task) {
                    resolve(task);
                },
                error: function (error) {
                    reject(null);
                }
            });
        })
    }

    // 1) pegar as urls das tasks do backend para verificar se existe mais tasks
    var updateTaskUrls = function () {        
        $.ajax({
            url: url,
            success: function (ids) {
                ids.forEach(function (taskId) {
                    if (!filterTaskIDsList(taskId)) {
                        taskIDsList.push(taskId);
                        addOrUpdateTask(taskId);
                    }
                });
            },
            error: function (error) {
                console.log(error);
            }
        });

        // Atualiza a lista de urls a cada 5 segundos
        setTimeout(updateTaskUrls, 5000);
    };

    // 2) pegar os dados das tasks a partir das urls e exibir na view
    var createTask = function (id) {
        $.ajax({
            url: `${url}/${id}`,
            success: function (task) {
                var task = taskModel.createTask(
                    id,
                    task.name,
                    task.total,
                    task.current,
                    task.status
                );
                taskUI.addTaskHTML(task);
            },
            error: function (error) {
                console.log(error);
            }
        });
    };

    // 3) periodicamente atualizar os dados das tasks com o backend a partir da url
    var updateTask = function (id) {
        $.ajax({
            url: `${url}/${id}`,
            success: function (newTask) {
                var task = taskModel.getTaskById(id);
                if (task !== null) {
                    if (newTask.state === 'success') {

                    } else {

                    }
                }
            },
            error: function (error) {
                console.log(error);
            }
        });
    };

    // 4) atualizar os dados de progresso da task na view

    // 5) remover a task quando estiver finalizada

    // 6) atualizar a view removendo a task finalizada

    // 7) verifcar o servidor para ver se existe mais tasks

    return {
        init: function () {

        }
    }
});

var showTasks = (function () {
    var elements = {
        totalTasks: document.getElementById('total-tasks-qty'),
        button: document.getElementById('show-notify'),
        closeButton: document.querySelector('.close__'),
        tasks: document.getElementById('tasks'),
        tasksContent: document.getElementById('task_list')
    };

    var data = {
        tasks: []
    }

    var toggleTasks = function () {
        $(elements.tasks).fadeToggle();
    }

    var addEvents = function () {
        elements.button.addEventListener('click', function (event) {
            toggleTasks();
        });

        elements.closeButton.addEventListener('click', function (event) {
            toggleTasks();
        });
    }

    var addTaskHTML = function (task) {
        var task = task;
        var currentPerc = parseInt((parseInt(task.current) * 100) / parseInt(task.total));
        
        var html = `
        <li id="task__${task.id}"> <p><b>Tarefa:</b>\r${task.name}\r<b>Status:</b>\r${task.current}/${task.total}</p>
            <div class="progress">
                <div class="progress-bar" role="progressbar" aria-valuenow="" aria-valuemin="0" aria-valuemax="100" style="width: ${currentPerc}%;">
                    ${currentPerc}%
                </div>
            </div>
        </li>
        `;

        elements.tasksContent.insertAdjacentHTML('beforeend', html);
    };

    var updateTaskHTML = function (task) {
        var taskElement = document.getElementById(`task__${task.id}`);
        var currentPerc = parseInt((parseInt(task.current) * 100) / parseInt(task.total));
        
        var html = `         
        <p><b>Tarefa:</b>\r${task.name}<b>\rStatus:</b>\r${task.current}/${task.total}</p>
        <div class="progress">
            <div class="progress-bar" role="progressbar" aria-valuenow="" aria-valuemin="0" aria-valuemax="100" style="width: ${currentPerc}%;">
                ${currentPerc}%
            </div>
        </div>
        `;

        taskElement.innerHTML = html;
    };

    var removeTaskHTML = function (task) {
        var taskElement = document.getElementById(`task__${task.id}`);
        taskElement.parentElement.removeChild(taskElement);
    }

    var clearTasks = function () {
        html = '<li><p>Não existem tarefas sendo processados.</p></li>'
        elements.tasksContent.innerHTML = html;
    }

    var addTasks = function (urls) {
        const url = '/tasks'
        // percorre a lista de urls retornadas
        setTimeout(function(){
            
        }, 5);
        $.ajax({
            url: url,
            success: function (taskUrls) {
                if (data.tasks.length > 0) {

                } else {
                    taskUrls.forEach(function (url) {

                    });
                }
            },
            error: function (error) {
                console.log(error);
            }
        });

        urls.forEach(function (url) {
            $.ajax({
                url: url,
                success: function(task) {
                    task.id = data.tasks.length + 1;
                    task.url = url;
                    data.tasks.push(task);
                    addTaskHTML(task);
                    updateTasks();

                    elements.totalTasks.textContent = data.tasks.length;
                },
                error: function(error) {
                    console.log(error);
                }
            });
        });
        
    };

    var updateTasks = function () {
        setTimeout(function () {
            if (data.tasks.length > 0) {
                data.tasks.forEach(function (task, index) {
                    $.ajax({
                        url: task.url,
                        success: function(result) {
    
                            task.current = result.current;
                            task.status = result.status;
                            task.state = result.state;
                            updateTaskHTML(task);
                            
                            if (task.state === 'success') {
                                removeTaskHTML(task);
                                data.tasks.splice(index, 1);
                            }
                        },
                        error: function(error) {
                            console.log(error);
                        }
                    });
                });
                updateTasks();
            } else {
                clearTasks();
            }
        }, 1000);
    };

    return {
        init: function () {
            addEvents()
        },

        addTasks: function(url) {
            addTasks(url);
        }
    };
});


/**
 *  Pagina: produtos/precos/atualizar
 *      Tela onde á atualizados os preços dos produtos
 */

 var precoModel = (function(){
    /**
     * Representa a model que vai conter todos os objetos das tarefas
     * em execução no backend
     */
    
    var Task = function (taskId, name, total, current, complete, errorsCount, errors, status) {
        this.id = taskId;
        this.name = name;
        this.total = total;
        this.current = current;
        this.complete = complete;
        this.errorsCount = errorsCount;
        this.errors = errors;
        this.status = status;
    };

    var task;

    return {
        // 1) criar Task
        createTask: function (data) {
            task = new Task(
                data.id,
                data.name,
                data.total,
                data.current,
                data.complete,
                data.errors_count,
                data.errors,
                data.status
            )
        },

        // 2) update task
        updateTask: function (current, complete, errorsCount, errors, status) {
            task.current = current;
            task.complete = complete;
            this.errorsCount = errorsCount;
            task.errors = errors;
            task.status = status;
        },

        // 3) get task
        getTask: function () {
            return task;
        }
    }
 });

 var precoUI = (function(){
     var elements = {
        taskTitle: document.getElementById('task-title'),
        taskPanel: document.getElementById('task-panel'),
        taskMessage: document.getElementById('task-message'),
        progressBar: document.getElementById('preco-progress-bar'),
        errorList: document.getElementById('error-list')
     }

     return {
         updateTaskHTML: function (task) {
            var currentPerc = parseInt((parseInt(task.current) * 100) / parseInt(task.total));

            var concluidos = task.complete === undefined ? 0 : task.complete;
            var erros = task.errorsCount === undefined ? 0 : task.errorsCount;

            elements.taskMessage.innerHTML = `
                <strong>Tarefas Executadas: </strong> &#32; ${task.current} &#32; de &#32; ${task.total} &#32;
                <strong>Status: </strong> &#32; ${task.status} &#32;
                <strong>Concluídos: </strong> &#32; ${concluidos} &#32;
                <strong>Erros: </strong> &#32; ${erros}
            `;
            
            elements.progressBar.style.width = `${currentPerc}%`;
            elements.progressBar.innerHTML = `${currentPerc}%`;

            if (task.errors.length > 0) {
                elements.errorList.innerHTML = '';

                task.errors.forEach( (error) => {
                    var htmlError = document.createElement('li');
                    htmlError.classList.add('list-group-item', 'list-group-item-danger');
                    htmlError.innerText = error;
                    elements.errorList.insertAdjacentElement('beforeend', htmlError);
                });
            }
         },

         addButton: function () {
             var button = document.createElement('a');
             button.href = window.location.pathname + '?clear_task=yes';
             button.innerHTML = 'Atualizar Pagina';
             button.classList.add('btn', 'btn-primary');

             elements.taskPanel.insertAdjacentElement('beforeend', button);
         },

         updateTitleText: function (text) {
            elements.taskTitle.innerText = text;
         }
     }
 });

 var precoControl = (function(){
     var model = precoModel();
     var ui = precoUI();
    
     // 1) iniciar a task a partir do id
     var initTask = function (taskId) {
        $.ajax({
            url: `/produtos/task/${taskId}`,
            success: (data) => {
                model.createTask(data);
                updateTasks();
            }
        });
     };

     // 2) atualizar o status da task
     var updateTasks = function () {
         var task = model.getTask();
         ui.updateTaskHTML(task);

         if (task.current < task.total) {
             setTimeout( () => {
                $.ajax({
                    url: `/produtos/task/${task.id}`,
                    success: (data) => {
                        model.updateTask(data.current, data.complete, data.errors_count, data.errors, data.status)
                        updateTasks();
                    }
                });
             }, 1000);
         } else {
            ui.addButton();
            ui.updateTitleText('Tarefa Completada');
         }
     };

     // 3) exibir tarefa finalizada quando a task for encerrada

     return {
         init: function (taskId) {
            initTask(taskId);
            // model.createTask(data);
         }
     }
 });


/*
*   Pagina: categorias/importar
*       Tela onde são listadas as categorias importadas do site
*       e onde é possivel atualizar as categorias
*/
var categoriaImportarControl = (function(){
    var urlApi = '/api/categorias';
    var data = [];

    // 1) pegar a lista de categorias
    var getCategorias = function() {
        $.ajax({
            url: urlApi,
            success: function(categorias) {
                data = categorias;
                data = convertToTreeView(data);
                showTreeView();
            },
            error: function(error) {
                console.log(error);
            }
        });
    }

    // 2) coverter para o formato utilizado pelo bootstrap-treeview
    var convertToTreeView = function(data) {
        var treeView = [];
        
        data.forEach(function(el){
            var categoria = {name: '', nodes: []};
            categoria.text = el.name;
            
            if (el.hasOwnProperty('childrens') && el.childrens.length) {
                categoria.nodes = convertToTreeView(el.childrens);
            }

            treeView.push(categoria)
        });

        return treeView;
    }

    // 3) iniciar o bootstrap-treeview
    var showTreeView = function() {
        $('#tree').treeview({data: data});
        $("#tree").show();
        $("#loading").delay(1000).fadeOut("slow");
    }

    return {
        init: function() {
            getCategorias();
        }
    }
})


/*
    Pagina: produtos/enviar    
    
*/

produtosEnviarModel = (function(){
    var data = {
        produtos: []
    };

    var Produto = function(id) {
        this.id = parseInt(id);
        this.secao = null;
        this.grupo = null;
        this.subgrupo = null;
    };

    Produto.prototype.addSecao = function(secao){
        if(secao !== null){
            this.secao = parseInt(secao);
        } else {
            this.secao = null;
        }
    };

    Produto.prototype.addGrupo = function(grupo){
        if (grupo !== null) {
            this.grupo = parseInt(grupo);
        } else {
            this.grupo = null;
        }
    };

    Produto.prototype.addSubGrupo = function(subgrupo){
        if (subgrupo !== null) {
            this.subgrupo = parseInt(subgrupo);
        } else {
            this.subgrupo = null;
        }
    };

    var buscarProduto = function(id) {
        for(x=0; x < data.produtos.length; x++){            
            produto = data.produtos[x];
            if(produto.id === parseInt(id)){
                return produto;
            }
        }
        return null;
    };

    var createProduct = function(id) {
        var produto = buscarProduto(id);
        if(produto === null){
            produto = new Produto(id);
            data.produtos.push(produto);
        }
        return produto;
    };

    return {
        addSecao: function(id, secao) {
            var produto = createProduct(id);
            produto.addSecao(secao);
            console.log(produto);
        },
        
        addGrupo: function(id, grupo) {
            var produto = createProduct(id);
            produto.addGrupo(grupo);
            console.log(produto);
        },

        addSubGrupo: function(id, subgrupo) {
            var produto = createProduct(id);
            produto.addSubGrupo(subgrupo);
            console.log(produto);
        },

        clear: function(id) {
            var produto = buscarProduto(id);
            console.log('produtosEnviarModel', produto);
            if(produto !== null) {
                produto.addSecao(null);
                produto.addGrupo(null);
                produto.addSubGrupo(null);
            }
            console.log('produtosEnviarModel', produto);
        },

        createProduct: createProduct,

        validarProdutos: function() {
            var produtos = data.produtos;
            var pendentes = [];

            for(x=0; x < produtos.length; x++) {
                var produto = produtos[x];

                console.log(!produto.secao || !produto.grupo || !produto.subgrupo);
                if(!produto.secao || !produto.grupo || !produto.subgrupo){
                    pendentes.push(produto.id);
                }
            }
            return pendentes;
        },

        getData: function() {
            return data;
        }
    }
});


produtosEnviarUI = (function(){
    const DOMelements = {
        form: document.getElementById('form-enviar-produto'),
        submit: document.getElementById('enviar'),
        secoes: Array.from($('.secoes')),
        grupos: Array.from($('.grupos')),
        subgrupos: Array.from($('.subgrupos'))
    };

    var addSelect = function(categorias, select) {
        var htmlOptions = '<option value="0">Selecione</option>\n';
        
        for(x=0; x < categorias.length; x++) {
            var categoria = categorias[x];
            var option = `<option value="${categoria.category_id}">${categoria.name}</option>\n`;
            htmlOptions += option;
        }

        select.innerHTML = htmlOptions;
        select.disabled = false;
        htmlOptions = '';
    }

    return {
        getDOMElements: () => {
            return DOMelements;
        },

        addSelectGrupo: (categorias, select) => {
            addSelect(categorias, select);
        },

        cleanSelect: function(select) {
            select.innerHTML = '';
            select.disabled = true;
        },

        validateForm: function(pendentes) {
            DOMelements.secoes.forEach(function(secao) {
                secao.parentNode.parentNode.classList.remove('red');
            });

            console.log(pendentes);
            for (x=0; x < pendentes.length; x++) {
                var row = document.getElementById('secao-' + pendentes[x]).parentNode.parentNode;
                row.classList.add('red');
            }
        }
    }
});


produtosEnviarControl = (function(){
    var ctrlUI = produtosEnviarUI();
    var ctrlModel = produtosEnviarModel();

    var buscarCategorias = function(parentID, select) {
        let path = `/produtos/enviar/categorias/${parentID}`;
        $.ajax({
            url: path,
            success: function(categorias) {
                ctrlUI.addSelectGrupo(categorias, select);
            },
            error: function(error) {
                console.log(error);
            }
        });
    };

    var validarFormulario = function() {
        pendentes = ctrlModel.validarProdutos();        
        if (pendentes.length) {
            ctrlUI.validateForm(pendentes);
            return false;
        }
        return true;
    };

    var initEvents = function() {
        var form = ctrlUI.getDOMElements().form;
        var submit = ctrlUI.getDOMElements().submit;
        var secoes = ctrlUI.getDOMElements().secoes;
        var grupos = ctrlUI.getDOMElements().grupos;
        var subgrupos = ctrlUI.getDOMElements().subgrupos;

        // Adiociona o evento para cancelar o envio do formulario
        // Para que seja realizado os devidos testes
        $(submit).on('click', (event) => {
            event.preventDefault();
            if (validarFormulario()) {
                console.log('teste');
            }
            form.submit();
        });
        
        secoes.forEach((secao) => {
            var id = secao.name.split('-')[1];
            ctrlModel.createProduct(id);

            $(secao).on('change', (event) => {
                var id = secao.name.split('-')[1];
                var value = secao.value;
                var select = document.getElementById('grupo-' + id);
                
                if (parseInt(value) !== 0) {
                    ctrlModel.addSecao(id, value);
                    buscarCategorias(value, select);
                } else {
                    ctrlUI.cleanSelect(select);
                    var subgrupo = document.getElementById('subgrupo-' + id);
                    ctrlUI.cleanSelect(subgrupo);
                    
                    ctrlModel.addSecao(id, null);
                    ctrlModel.addGrupo(id, null);
                    ctrlModel.addSubGrupo(id, null);
                }
            });
        });

        grupos.forEach((grupo) => {
            $(grupo).on('change', (event) => {
                var id = grupo.name.split('-')[1];
                var value = grupo.value;
                var select = document.getElementById('subgrupo-' + id);

                if (parseInt(value) !== 0) {
                    ctrlModel.addGrupo(id, value);
                    buscarCategorias(value, select);
                } else {
                    ctrlUI.cleanSelect(select);
                    
                    ctrlModel.addGrupo(id, null);
                    ctrlModel.addSubGrupo(id, null);
                }
            });
        });

        subgrupos.forEach((sugrupo) => {
            $(sugrupo).on('change', (event) => {
                var id = sugrupo.name.split('-')[1];
                var value = sugrupo.value;

                if (parseInt(value) !== 0) {
                    ctrlModel.addSubGrupo(id, value);
                } else {
                    ctrlModel.addSubGrupo(id, null);
                }
            });
        });
    }

    return {
        init: () => {
            initEvents();
        }
    }
});